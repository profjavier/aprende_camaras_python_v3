# app.py

# Librería para captura y procesamiento de vídeo (OpenCV)
import cv2

# Flask: framework web
from flask import Flask, render_template, Response

# Configuración general de la app
from config import Config

# Extensiones de base de datos y login
from extensions import db, login_manager

# Blueprints (módulos de autenticación)
from routes_auth import auth_bp

# Modelo de usuario
from models import User

# Decorador para control de roles (seguridad)
from utils.security import role_required

# Control de sesiones de usuario
from flask_login import login_required


# ---------------------------
# CREACIÓN DE LA APLICACIÓN
# ---------------------------
app = Flask(__name__)
app.config.from_object(Config)


# ---------------------------
# CAPTURA DE CÁMARA WEB
# ---------------------------
# 0 = cámara por defecto del sistema
camera = cv2.VideoCapture(0)


# ---------------------------
# GENERADOR DE FRAMES (STREAMING)
# ---------------------------
def generar_frames():
    while True:
        # Captura un frame desde la cámara
        success, frame = camera.read()

        # Si falla la cámara, se detiene el bucle
        if not success:
            break
        else:
            # ---------------------------
            # CONVERSIÓN DE IMAGEN
            # ---------------------------
            # Convierte el frame (matriz OpenCV) a formato JPEG comprimido
            ret, buffer = cv2.imencode('.jpg', frame)

            # Convierte la imagen a bytes (formato enviable por HTTP)
            frame = buffer.tobytes()

            # ---------------------------
            # STREAMING CON YIELD
            # ---------------------------
            # En lugar de devolver todo de golpe,
            # yield envía cada frame uno a uno al navegador
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# ---------------------------
# INICIALIZACIÓN DE EXTENSIONES
# ---------------------------
db.init_app(app)
# carga la configuración de Flask desde la clase Config
login_manager.init_app(app)

# Página a la que se redirige si el usuario no está logueado
login_manager.login_view = 'auth.login'


# ---------------------------
# CARGADOR DE USUARIO (FLASK-LOGIN)
# ---------------------------
@login_manager.user_loader
def load_user(user_id):
    # Busca el usuario en la base de datos por ID
    return db.session.get(User, int(user_id))

# ---------------------------
# REGISTRO DE BLUEPRINTS
# ---------------------------
app.register_blueprint(auth_bp)


# ---------------------------
# CREAR TABLAS EN LA BD
# ---------------------------
with app.app_context():
    db.create_all()


# ---------------------------
# RUTA PRINCIPAL (STREAM DE VÍDEO)
# ---------------------------
@app.route('/')
@login_required           # el usuario debe estar logueado
@role_required('ADMIN')   # solo usuarios ADMIN pueden acceder
def index():
    # Response convierte el generador en un stream HTTP continuo
    return Response(
        generar_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


# ---------------------------
# MANEJO DE ERRORES
# ---------------------------

# Error 404 - página no encontrada
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


# Error 401 - no autorizado (ojo: aquí tenías bug antes)
@app.errorhandler(401)
def not_found_error(error):
    return render_template('errors/401.html'), 401


# Error 403 - prohibido
@app.errorhandler(403)
def not_found_error(error):
    return render_template('errors/403.html'), 403


# Error 500 - error interno del servidor
@app.errorhandler(500)
def internal_error(error):
    # rollback por si hay fallo en la BD
    db.session.rollback()
    return render_template('errors/500.html'), 500


# ---------------------------
# EJECUCIÓN DE LA APP
# ---------------------------
if __name__ == '__main__':
    app.run(debug=True)