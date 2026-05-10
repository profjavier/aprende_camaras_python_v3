import cv2
import tkinter as tk
from PIL import Image, ImageTk
from pytapo import Tapo
from datetime import datetime
import os

IP_CAMARA = '192.168.1.36'  # CEPY07
IP_CAMARA = '192.168.1.136' # CEPY08
USUARIO_LOCAL = 'cepy2026'
CONTRASENA_LOCAL = 'Castelar2026'

print(f"Intentando conectar a {IP_CAMARA}")
print(f"Usuario: {USUARIO_LOCAL}")
print(f"Contraseña: {'*' * len(CONTRASENA_LOCAL)}")

try:
    # Crear instancia de Tapo
    tapo = Tapo(IP_CAMARA, USUARIO_LOCAL, CONTRASENA_LOCAL)

    # Obtener información básica
    info = tapo.getBasicInfo()
    print("\n✓ Conexión exitosa!")
    print(f"Nombre de la cámara: {info.get('device_info', {}).get('device_name', 'No disponible')}")
    print(f"Modelo: {info.get('device_info', {}).get('model', 'No disponible')}")
    print(f"Firmware: {info.get('device_info', {}).get('fw_ver', 'No disponible')}")

    # Obtener la URL del stream RTSP
    # Nota: Necesitarás habilitar RTSP en la configuración de la cámara primero
    rtsp_url = f"rtsp://{USUARIO_LOCAL}:{CONTRASENA_LOCAL}@{IP_CAMARA}:554/stream1"
    print(f"\nURL RTSP: {rtsp_url}")

    # Probar captura de video con OpenCV
    print("\nProbando captura de video...")
    cap = cv2.VideoCapture(rtsp_url)

    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print("✓ Video capturado correctamente")
            # Guardar una imagen de prueba
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"captura_{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            print(f"✓ Imagen guardada como {filename}")
        else:
            print("✗ No se pudo leer el frame")
        cap.release()
    else:
        print("✗ No se pudo abrir el stream RTSP")
        print("  Asegúrate de haber habilitado RTSP en la configuración de la cámara:")
        print("  1. Abre la app Tapo")
        print("  2. Ve a la configuración de la cámara")
        print("  3. Busca 'Configuración avanzada' → 'Cuenta de cámara'")
        print("  4. Habilita 'Autenticación RTSP'")

except Exception as err:
    print(f"\n✗ Error: {err}")
    print("\nPosibles soluciones:")
    print("1. Verifica que la cámara esté encendida y conectada a la red")
    print("2. Confirma la IP: ¿es correcta 192.168.1.36?")
    print("3. Prueba hacer ping a la cámara:")
    os.system("ping 192.168.1.36 -n 2")
    print("\n4. Si el problema persiste, intenta reiniciar la cámara")