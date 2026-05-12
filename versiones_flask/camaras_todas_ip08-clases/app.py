import os
from logging.handlers import RotatingFileHandler
import logging

from flask import Flask, render_template, Response

from config import Config
from extensions import db, login_manager

from routes_auth import auth_bp
from models import User
from utils.security import role_required
from flask_login import login_required

from camara_stream import CamaraStream


app = Flask(__name__)
app.config.from_object(Config)

# -----------------------
# LOGGER
# -----------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(LOG_DIR, "cepy.log")
os.makedirs(LOG_DIR, exist_ok=True)

app.logger.handlers.clear()
handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
handler.setFormatter(logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# -----------------------
# CAMARAS (CLASE)
# -----------------------
stream = CamaraStream(app.logger)
stream.inicializar("config_camaras.cfg")

# -----------------------
# FLASK EXTENSIONS
# -----------------------
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

# -----------------------
# ROUTES
# -----------------------
@app.route('/')
@login_required
@role_required('ADMIN')
def index():
    return render_template(
        "index.html",
        camaras=stream.get_camaras()
    )

@app.route('/cam/<cam_id>')
@login_required
@role_required('ADMIN')
def camara(cam_id):
    return Response(
        stream.generar_frames(cam_id),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )

@app.route('/camaras')
@login_required
@role_required('ADMIN')
def camaras():
    return render_template(
        "camaras.html",
        camaras=stream.get_camaras()
    )

# -----------------------
# ERRORES
# -----------------------
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
    app.run(debug=True, host="0.0.0.0", port=5000)