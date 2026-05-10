from pytapo import Tapo

IP_CAMARA = '192.168.1.36'
# Intenta con estas combinaciones:
# Opción 1: Email de la cuenta y contraseña de la cámara
USUARIO = "cepycastelar@gmail.com"
CONTRASENA = "Castelar2026"  # Esta debe ser la contraseña de la cámara, no de la cuenta Tapo

# Opción 2: Usuario "admin" si nunca configuraste usuario
USUARIO = "cepy2026"
CONTRASENA = "Castelar2026"

tapo = Tapo(IP_CAMARA, USUARIO, CONTRASENA)

try:
    info = tapo.getBasicInfo()
    print("Conexión exitosa!")
    print(info)
except Exception as e:
    print(f"Error: {e}")