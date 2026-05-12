from onvif import ONVIFCamera
import cv2
import time

# ======================
# CONFIG CAMARA
# ======================
ip = '192.168.60.153'
ip = '192.168.1.105'
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
# VIDEO STREAM
# ======================
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("❌ No se puede abrir el stream RTSP")
    exit()

print("""
🎮 CONTROLES:
W = arriba
S = abajo
A = izquierda
D = derecha
Q = salir
""")

while True:
    ret, frame = cap.read()

    if not ret:
        print("⚠️ Error leyendo vídeo")
        break

    cv2.imshow("Camara Tapo PTZ", frame)

    key = cv2.waitKey(1) & 0xFF

    # controles
    if key == ord('w'):
        move(0, 0.5)
        time.sleep(0.3)
        stop()

    elif key == ord('s'):
        move(0, -0.5)
        time.sleep(0.3)
        stop()

    elif key == ord('a'):
        move(-0.5, 0)
        time.sleep(0.3)
        stop()

    elif key == ord('d'):
        move(0.5, 0)
        time.sleep(0.3)
        stop()

    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
stop()