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


# Captura de la webcam (0 = webcam por defecto)
camera = cv2.VideoCapture(
    "rtsp://cepy2026:Castelar2026@192.168.60.153:554/Streaming/stream2"
)

def generar_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Codificar frame como JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')



# init extensiones
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# registrar blueprints
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

@app.route('/')
@login_required
@role_required('ADMIN')
def index():
    return Response(generar_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


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