'''pip install flask pyqt6 opencv-python onvif-zeep'''

from flask import Flask, Response, render_template_string, request
import cv2
from onvif import ONVIFCamera

# ======================
# CONFIG
# ======================
ip = '192.168.60.153'
port = 2020
user = 'cepy2026'
password = 'Castelar2026'

rtsp_url = f"rtsp://{user}:{password}@{ip}:554/stream1"

# ======================
# ONVIF PTZ
# ======================
camera = ONVIFCamera(ip, port, user, password)
media = camera.create_media_service()
ptz = camera.create_ptz_service()
profile = media.GetProfiles()[0]
token = profile.token


def move(x, y):
    request = ptz.create_type('ContinuousMove')
    request.ProfileToken = token
    request.Velocity = {
        'PanTilt': {'x': x, 'y': y},
        'Zoom': {'x': 0}
    }
    ptz.ContinuousMove(request)


def stop():
    ptz.Stop({'ProfileToken': token})


# ======================
# FLASK
# ======================
app = Flask(__name__)

cap = cv2.VideoCapture(rtsp_url)


def generate():
    while True:
        success, frame = cap.read()
        if not success:
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


HTML = """
<html>
<head>
    <title>Tapo PTZ Web</title>
</head>
<body style="text-align:center;background:#111;color:white;">

<h2>📷 Cámara PTZ Web</h2>

<img src="/video" width="640">

<br><br>

<button onclick="fetch('/move/up')">⬆</button>
<button onclick="fetch('/move/stop')">⏹</button>
<button onclick="fetch('/move/down')">⬇</button>
<br><br>
<button onclick="fetch('/move/left')">⬅</button>
<button onclick="fetch('/move/right')">➡</button>

</body>
</html>
"""


@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/video')
def video():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/move/<direction>')
def move_camera(direction):

    if direction == "up":
        move(0, 0.5)

    elif direction == "down":
        move(0, -0.5)

    elif direction == "left":
        move(-0.5, 0)

    elif direction == "right":
        move(0.5, 0)

    elif direction == "stop":
        stop()

    return "OK"


# ======================
# RUN
# ======================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)