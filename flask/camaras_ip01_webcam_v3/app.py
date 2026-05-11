# app.py

from os import abort

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

from webcam import Webcam


# ---------------------------
# CREACIÓN DE LA APLICACIÓN
# ---------------------------
app = Flask(__name__)
# carga la configuración de Flask desde la clase Config
app.config.from_object(Config)

try:
    webcam = Webcam()
    webcam.iniciar()
except:
    print('Error al iniciar webcam')
    abort()

# ---------------------------
# INICIALIZACIÓN DE EXTENSIONES
# ---------------------------
db.init_app(app)
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
# ---------------------------
# PÁGINA PRINCIPAL
# ---------------------------
@app.route('/')
@login_required
@role_required('ADMIN')
def index():
    return render_template('index.html-BASE')


# ---------------------------
# STREAM DE VÍDEO
# ---------------------------
@app.route('/video')
@login_required
@role_required('ADMIN')
def video():
    # Devuelve stream MJPEG
    return Response(
        webcam.generar_frames(),
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