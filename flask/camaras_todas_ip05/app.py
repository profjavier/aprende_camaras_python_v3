import os

import cv2
from flask import Flask, render_template, Response

from config import Config
from extensions import db, login_manager

# importar blueprints
from routes_auth import auth_bp

from models import User
from utils.security import role_required
from flask_login import login_required

app = Flask(__name__)
app.config.from_object(Config)


def cargar_camaras(ruta):
    camaras = []

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

    return camaras

def get_rtsp(cam):
    return f"rtsp://{cam['user']}:{cam['password']}@{cam['ip']}:{cam['port']}/Streaming/stream2"

camaras_config = cargar_camaras("config_camaras.cfg")

camaras_stream = {
    cam["id"]: cv2.VideoCapture(get_rtsp(cam))
    for cam in camaras_config
}

def generar_frames(cam_id):
    camera = camaras_stream[cam_id]

    while True:
        success, frame = camera.read()
        if not success:
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



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

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(401)
def not_found_error(error):
    return render_template('errors/401.html'), 404

@app.errorhandler(403)
def not_found_error(error):
    return render_template('errors/403.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)