import os
import threading
from logging.handlers import RotatingFileHandler

import logging
from flask import Flask, render_template, Response

from versiones_flask.camaras_todas_ip10.config_app import ConfigApp
from extensions import db, login_manager
from camaras_config import CamarasConfig

# importar blueprints
from routes_auth import auth_bp

from models import User
from utils.security import role_required
from flask_login import login_required

from camara import Camara



# logging.basicConfig(
#     filename = LOG_FILE,
#     level = logging.INFO,
#     format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
# )
#Si se utiliza logging de flask no hace falta esta asignacion
# logger = logging.getLogger(__name__)


app = Flask(__name__)
app.config.from_object(ConfigApp)

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
    return render_template("index.html", camaras=camaras_activas)

@app.route('/cam/<cam_id>')
@login_required
@role_required('ADMIN')
def camara(cam_id):
    return Response(
        camara.generar_frames(cam_id),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/camaras')
@login_required
@role_required('ADMIN')
def camaras():
    return render_template("camaras.html", camaras=camaras_activas)

@app.route("/ping")
def ping():
    camara.ping()
    return "ok"


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

    camara = Camara(app)
    camaras_config = CamarasConfig(app,"config")
    # camaras_config = camara.cargar_camaras("config_camaras.cfg")

    for cam in camaras_config.camaras_activas:
        cam_id = cam["id"]
        camara.frames[cam_id] = None
        camara.locks[cam_id] = threading.Lock()

    camaras_activas = camaras_config.camaras_activas
    camara.camaras_activas = camaras_config.camaras_activas

    camara.inicializar_camaras() 

    app.run(debug=True, port=5000, host="0.0.0.0")