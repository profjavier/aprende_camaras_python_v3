'''pip install onvif-zeep'''
from onvif import ONVIFCamera
import time

# Datos de tu cámara
ip = '192.168.60.153'
port = 2020
user = 'cepy2026'
password = 'Castelar2026'

camera = ONVIFCamera(ip, port, user, password)

# Servicios
media = camera.create_media_service()
ptz = camera.create_ptz_service()

# Perfil de video
profiles = media.GetProfiles()
profile = profiles[0]

token = profile.token

# Movimiento PTZ
request = ptz.create_type('ContinuousMove')
request.ProfileToken = token

# Mover derecha
request.Velocity = {
    'PanTilt': {'x': 0.5, 'y': 0},
    'Zoom': {'x': 0}
}

ptz.ContinuousMove(request)

time.sleep(2)

# Parar movimiento
ptz.Stop({'ProfileToken': token})