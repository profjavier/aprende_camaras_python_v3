import cv2
import time

# --- CONFIGURACIÓN ---+
USUARIO = 'javier'  # El que creaste en la App Tapo
PASSWORD = 'Castelar2026'  # El que creaste en la App Tapo
IP_CAMARA = '192.168.1.200'
PUERTO = '554'  # Puerto RTSP estándar

# Stream1 es 2K (Alta calidad), Stream2 es 360p (Baja calidad/Fluido)
rtsp_url = f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAMARA}:{PUERTO}/stream1"


def conectar_camara():
    print(f"Conectando a Tapo C210 en {IP_CAMARA}...")
    cap = cv2.VideoCapture(rtsp_url)

    # Optimizaciones para reducir latencia
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

    if not cap.isOpened():
        print("Error: No se pudo abrir el flujo de video.")
        return None
    return cap


def main():
    cap = conectar_camara()
    if not cap: return

    print("Conexión exitosa. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Se perdió la señal. Intentando reconectar en 5 segundos...")
            cap.release()
            time.sleep(5)
            cap = conectar_camara()
            if not cap: break
            continue

        # Opcional: Redimensionar la ventana si el 2K es muy grande para tu monitor
        # frame = cv2.resize(frame, (1280, 720))

        cv2.imshow('Tapo C210 - Python Live View', frame)

        # Salir con la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Streaming finalizado.")


if __name__ == "__main__":
    main()