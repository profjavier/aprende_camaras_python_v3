from flask import Flask, render_template, Response, redirect, url_for
import cv2
from datetime import datetime
import os

app = Flask(__name__)

# ---------------- CONFIGURACIÓN ----------------
# --- CONFIGURACIÓN ---
USUARIO = 'javier'  # El que creaste en la App Tapo
PASSWORD = 'Castelar2026'  # El que creaste en la App Tapo
IP_CAMARA = '192.168.1.200'
PUERTO = '554'  # Puerto RTSP estándar
RTSP_URL = f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAMARA}:{PUERTO}/stream1"

SAVE_DIR = os.path.join('static', 'capturas')
os.makedirs(SAVE_DIR, exist_ok=True)
# -----------------------------------------------
cap = cv2.VideoCapture(RTSP_URL)
last_frame = None

def gen_frames():
    global last_frame
    while True:
        success, frame = cap.read()
        if not success:
            continue
        last_frame = frame.copy()
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def index():
    # Lista solo la última foto capturada
    fotos = sorted(os.listdir(SAVE_DIR))
    ultima = fotos[-1] if fotos else None
    return render_template('index.html', ultima_foto=ultima)

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture')
def capture():
    global last_frame
    if last_frame is not None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = os.path.join(SAVE_DIR, f'foto_{ts}.jpg')
        cv2.imwrite(path, last_frame)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=40000, debug=True)