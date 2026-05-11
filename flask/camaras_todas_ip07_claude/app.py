import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from flask import Flask, render_template, Response, jsonify, abort
from flask_login import login_required

from config import Config
from extensions import db, login_manager
from routes_auth import auth_bp
from models import User
from utils.security import role_required

from camara import Camara   # ← clase nueva

# ---------------------------------------------------------------------------
# Estado global de cámaras
# ---------------------------------------------------------------------------
camaras: dict[str, Camara] = {}   # { cam_id: Camara }

# ---------------------------------------------------------------------------
# Helpers de configuración
# ---------------------------------------------------------------------------

def cargar_camaras(ruta: str) -> list[Camara]:
    """Lee config_camaras.cfg y devuelve una lista de instancias Camara."""
    resultado = []
    app.logger.info(f"Cargando cámaras desde {ruta}")
    try:
        with open(ruta, "r") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                cam = Camara.desde_linea(linea, logger=app.logger)
                resultado.append(cam)
        app.logger.info(f"{len(resultado)} cámara(s) cargada(s)")
    except Exception:
        app.logger.exception("Error cargando cámaras")
    return resultado


def inicializar_camaras(ruta: str = "config_camaras.cfg") -> None:
    """Carga la config, instancia las cámaras y arranca sus hilos."""
    global camaras
    lista = cargar_camaras(ruta)
    camaras = {cam.id: cam for cam in lista}
    for cam in camaras.values():
        cam.iniciar()

# ---------------------------------------------------------------------------
# Aplicación Flask
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config.from_object(Config)

# — Logger rotante —
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR  = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(LOG_DIR, "cepy.log")
os.makedirs(LOG_DIR, exist_ok=True)

app.logger.handlers.clear()
handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3)
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter("%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# — Extensiones —
db.init_app(app)
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# — Blueprints —
app.register_blueprint(auth_bp)

with app.app_context():
    db.create_all()

# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------

@app.route("/")
@login_required
@role_required("ADMIN")
def index():
    return render_template("index.html-BASE", camaras=list(camaras.values()))


@app.route("/camaras")
@login_required
@role_required("ADMIN")
def vista_camaras():
    return render_template("camaras.html", camaras=list(camaras.values()))


@app.route("/cam/<cam_id>")
@login_required
@role_required("ADMIN")
def stream_camara(cam_id):
    cam = camaras.get(cam_id)
    if cam is None:
        abort(404)
    return Response(
        cam.generar_frames_mjpeg(),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


@app.route("/cam/<cam_id>/snapshot", methods=["POST"])
@login_required
@role_required("ADMIN")
def snapshot_camara(cam_id):
    """Captura una instantánea de la cámara y devuelve la ruta del fichero."""
    cam = camaras.get(cam_id)
    if cam is None:
        abort(404)

    ruta = cam.capturar_instantanea()
    if ruta is None:
        return jsonify({"error": "Sin frame disponible"}), 503

    return jsonify({"archivo": str(ruta)}), 201


# ---------------------------------------------------------------------------
# Manejadores de error
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404

@app.errorhandler(401)
def unauthorized_error(error):
    return render_template("errors/401.html"), 401

@app.errorhandler(403)
def forbidden_error(error):
    return render_template("errors/403.html"), 403

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("errors/500.html"), 500


# ---------------------------------------------------------------------------
# Entrada principal
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app.logger.info("Iniciando aplicación")
    inicializar_camaras("config_camaras.cfg")
    app.run(debug=False, port=5000, host="0.0.0.0")