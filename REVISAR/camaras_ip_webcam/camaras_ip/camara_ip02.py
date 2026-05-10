import cv2

# --- CONFIGURACIÓN ---
USUARIO = 'javier'  # El que creaste en la App Tapo
PASSWORD = 'Castelar2026'  # El que creaste en la App Tapo
IP_CAMARA = '192.168.1.200'
PUERTO = '554'  # Puerto RTSP estándar

# Stream1 es 2K (Alta calidad), Stream2 es 360p (Baja calidad/Fluido)
rtsp_url = f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAMARA}:{PUERTO}/stream1"

cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("❌ No se pudo conectar a la cámara")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ No se pudo leer el stream")
        break

    cv2.imshow("Tapo C210", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
