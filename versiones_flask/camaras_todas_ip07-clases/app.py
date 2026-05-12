import os
import time
from logging.handlers import RotatingFileHandler

import cv2
import logging
from flask import Flask, render_template, Response

from config import Config
from extensions import db, login_manager

# importar blueprints
from routes_auth import auth_bp

from models import User
from utils.security import role_required
from flask_login import login_required

import threading

camaras_config = []
frames = {}
locks = {}

def capturar_camara(cam):
    cam_id = cam["id"]

    while True:
        cap = cv2.VideoCapture(get_rtsp(cam), cv2.CAP_FFMPEG)

        if not cap.isOpened():
            app.logger.warning(f"No conecta cámara {cam_id}")
            time.sleep(2)
            continue

        while True:
            success, frame = cap.read()

            if not success:
                app.logger.warning(f"Cámara {cam_id} caída")
                break

            # 🔴 AQUÍ ES DONDE VA
            _, buffer = cv2.imencode('.jpg', frame)
            buffer_jpeg = buffer.tobytes()

            with locks[cam_id]:
                frames[cam_id] = buffer_jpeg

            time.sleep(0.03)



# logging.basicConfig(
#     filename = LOG_FILE,
#     level = logging.INFO,
#     format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
# )
#Si se utiliza logging de flask no hace falta esta asignacion
# logger = logging.getLogger(__name__)


app = Flask(__name__)
app.config.from_object(Config)

# iniciar logger
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(LOG_DIR, "cepy.log")
os.makedirs(LOG_DIR, exist_ok=True)
# limpiar handlers previos de Flask
app.logger.handlers.clear()
handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
handler.setFormatter(formatter)

app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)



# camaras_config = []
camaras_stream = {}

def iniciar_hilos_camaras():
    for cam in camaras_config:
        t = threading.Thread(
            target=capturar_camara,
            args=(cam,),
            daemon=True
        )
        t.start()


def inicializar_camaras():
    global camaras_config

    camaras_config = cargar_camaras("config_camaras.cfg")

    for cam in camaras_config:
        cam_id = cam["id"]

        # frames[cam_id] = None
        # locks[cam_id] = threading.Lock()
        frames.setdefault(cam_id, None)
        locks.setdefault(cam_id, threading.Lock())

        t = threading.Thread(
            target=capturar_camara,
            args=(cam,),
            daemon=True
        )
        t.start()

def cargar_camaras(ruta):
    camaras = []

    app.logger.info(f"Cargando cámaras desde {ruta}")

    try:
        with open(ruta, "r") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue

                id_cam, ip, mac, port, user, password = linea.split(":")

                camaras.append({
                    "id": id_cam,
                    "ip": ip,
                    "mac": mac,
                    "port": int(port),
                    "user": user,
                    "password": password
                })
        app.logger.info(f"Camaras cargadas")
    except Exception as e:
        app.logger.exception("Error cargando cámaras")

    return camaras

def get_rtsp(cam):
    return f"rtsp://{cam['user']}:{cam['password']}@{cam['ip']}:{cam['port']}/Streaming/stream2"


def generar_frames(cam_id):
    while True:
        with locks[cam_id]:
            frame = frames.get(cam_id)

        if frame is None:
            continue

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
        )


# init extensiones
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# registrar blueprints
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

@app.route('/')
@login_required
@role_required('ADMIN')
def index():
    return render_template("index.html", camaras=camaras_config)

@app.route('/cam/<cam_id>')
@login_required
@role_required('ADMIN')
def camara(cam_id):
    return Response(
        generar_frames(cam_id),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/camaras')
@login_required
@role_required('ADMIN')
def camaras():
    return render_template("camaras.html", camaras=camaras_config)



@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template('errors/401.html'), 401

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500


if __name__ == '__main__':
    app.logger.info("Iniciando aplicación")

    camaras_config = cargar_camaras("config_camaras.cfg")

    for cam in camaras_config:
        cam_id = cam["id"]

        frames[cam_id] = None
        locks[cam_id] = threading.Lock()

    iniciar_hilos_camaras()

    app.run(debug=False, port=5000, host="0.0.0.0")
