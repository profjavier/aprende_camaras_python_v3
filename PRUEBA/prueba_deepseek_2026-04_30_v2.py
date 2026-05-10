#!/usr/bin/env python3
"""
Script para conectar y mover la cámara Tapo C210 usando ONVIF (puerto 2020) y RTSP (puerto 554).
"""

import cv2
import time
from threading import Thread
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# --- Intento de importación robusta para ONVIF ---
try:
    from onvif import ONVIFCamera

    ONVIF_AVAILABLE = True
    print("Biblioteca 'onvif-zeep' encontrada.")
except ImportError:
    ONVIF_AVAILABLE = False
    print("ADVERTENCIA: 'onvif-zeep' no instalada. El movimiento PTZ no estará disponible.")
    print("Ejecuta: pip install onvif-zeep")


class TapoC210ONVIF:
    def __init__(self, ip, username, password):
        """
        Inicializa el controlador para los puertos estándar 554 (RTSP) y 2020 (ONVIF).
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.onvif_cam = None
        self.ptz_service = None
        self.profile_token = None

        # URLs con los puertos correctos
        self.rtsp_url = f"rtsp://{username}:{password}@{ip}:554/stream1"
        self.onvif_url = f"http://{ip}:2020/onvif/device_service"
        print(f"[*] Usando RTSP: {self.rtsp_url.replace(password, '***')}")
        print(f"[*] Usando ONVIF: {self.onvif_url}")

    def init_onvif(self):
        """Inicializa la conexión y el servicio PTZ a través del puerto 2020."""
        if not ONVIF_AVAILABLE:
            print("[✗] ONVIF no está disponible. Movimiento deshabilitado.")
            return False

        try:
            print("[*] Conectando al servicio ONVIF en el puerto 2020...")
            # La IP, puerto 2020, usuario y contraseña de la "Cuenta de cámara"
            self.onvif_cam = ONVIFCamera(self.ip, 2020, self.username, self.password)

            # Crear servicio PTZ para mover la cámara
            self.ptz_service = self.onvif_cam.create_ptz_service()

            # Obtener el perfil de medios de la cámara
            media_service = self.onvif_cam.create_media_service()
            profiles = media_service.GetProfiles()

            if not profiles:
                print("[✗] No se encontraron perfiles ONVIF.")
                return False

            self.profile_token = profiles[0].token
            print(f"[✓] ONVIF inicializado correctamente en el puerto 2020. Perfil: {self.profile_token}")
            return True
        except Exception as e:
            print(f"[✗] Error ONVIF en puerto 2020: {e}")
            print("    Verifica que la 'Cuenta de cámara' esté ACTIVADA en la app de Tapo.")
            print("    Y que el usuario/contraseña sean los que creaste en ese paso.")
            return False

    def move_relative(self, x, y):
        """
        Mueve la cámara de forma relativa.
        x: -1 (izquierda) a 1 (derecha)
        y: -1 (abajo) a 1 (arriba)
        """
        if not self.ptz_service or not self.profile_token:
            if not self.init_onvif():
                return False

        try:
            request = self.ptz_service.create_type('RelativeMove')
            request.ProfileToken = self.profile_token
            request.Translation = {
                'PanTilt': {'x': x, 'y': y},
                'Zoom': {'x': 0}
            }
            self.ptz_service.RelativeMove(request)
            print(f"[✓] Movimiento ONVIF: x={x}, y={y}")
            return True
        except Exception as e:
            print(f"[✗] Error en el movimiento: {e}")
            return False

    def get_frame(self):
        """Captura un frame de video usando el puerto RTSP 554."""
        try:
            # Añadimos opciones para hacer la conexión más robusta
            cap = cv2.VideoCapture(self.rtsp_url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                print(f"[!] No se pudo abrir el stream RTSP en {self.ip}:554")
                return None
            ret, frame = cap.read()
            cap.release()
            if ret:
                return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            else:
                print("[!] Error al leer el frame del stream RTSP.")
        except Exception as e:
            print(f"[✗] Error de RTSP: {e}")
        return None


class ControlGUI:
    def __init__(self, camera):
        self.camera = camera
        self.root = tk.Tk()
        self.root.title("Control Tapo C210 v2 - ONVIF/RTSP")
        self.root.geometry("700x550")

        self.video_label = ttk.Label(self.root)
        self.video_label.pack(pady=10)

        # Frame de botones PTZ
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=20)

        # Estilo de los botones
        style = {"width": 10, "height": 2}

        self.btn_up = ttk.Button(btn_frame, text="▲ ARRIBA ▲", command=lambda: self.camera.move_relative(0, 0.5),
                                 **style)
        self.btn_up.grid(row=0, column=1, padx=5, pady=5)

        self.btn_left = ttk.Button(btn_frame, text="◄ IZQUIERDA ◄", command=lambda: self.camera.move_relative(-0.5, 0),
                                   **style)
        self.btn_left.grid(row=1, column=0, padx=5, pady=5)

        self.btn_stop = ttk.Button(btn_frame, text="■ DETENER ■", command=lambda: self.camera.move_relative(0, 0),
                                   **style)
        self.btn_stop.grid(row=1, column=1, padx=5, pady=5)

        self.btn_right = ttk.Button(btn_frame, text="► DERECHA ►", command=lambda: self.camera.move_relative(0.5, 0),
                                    **style)
        self.btn_right.grid(row=1, column=2, padx=5, pady=5)

        self.btn_down = ttk.Button(btn_frame, text="▼ ABAJO ▼", command=lambda: self.camera.move_relative(0, -0.5),
                                   **style)
        self.btn_down.grid(row=2, column=1, padx=5, pady=5)

        self.status = ttk.Label(self.root, text="Conectando...", relief=tk.SUNKEN)
        self.status.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # Iniciar el bucle de video
        self.update_video()

    def update_video(self):
        """Actualiza el frame de video periódicamente."""
        frame = self.camera.get_frame()
        if frame is not None:
            # Redimensionar para la GUI
            height, width = frame.shape[:2]
            if width > 640:
                scale = 640 / width
                new_size = (int(width * scale), int(height * scale))
                frame = cv2.resize(frame, new_size)

            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=image)
            self.video_label.config(image=photo)
            self.video_label.image = photo
            self.status.config(text="✓ Conectado y mostrando video (puerto 554)")
        else:
            self.status.config(text="⚠️ Error de conexión: No se recibe video. Verifica IP/Credenciales.")

        # Llamar a esta función de nuevo en 30ms
        self.root.after(30, self.update_video)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    print("\n=== CONTROLADOR TAPO C210 v2 (ONVIF/RTSP) ===\n")
    print("IMPORTANTE: Antes de ejecutar, activa la 'Cuenta de cámara' en la app Tapo.")
    print("Usa el usuario y contraseña que creaste allí, NO los de tu WiFi.\n")

    ip = input("IP de la cámara (ej: 192.168.60.153): ").strip()
    username = input("Usuario de la 'Cuenta de cámara' (app Tapo): ").strip()
    password = input("Contraseña de la 'Cuenta de cámara': ").strip()

    # Crear el controlador con los puertos correctos
    camera = TapoC210ONVIF(ip, username, password)

    # Comprobar si funciona el RTSP antes de abrir la GUI
    print("\n[*] Probando conexión RTSP (puerto 554)...")
    test_frame = camera.get_frame()
    if test_frame is not None:
        print("[✓] Conexión RTSP exitosa. Abriendo interfaz gráfica...")
        gui = ControlGUI(camera)
        gui.run()
    else:
        print("\n[✗] ERROR CRÍTICO: No se pudo conectar al stream RTSP.")
        print("    *****************************************************")
        print("    VERIFICA ESTOS 3 PUNTOS (SON OBLIGATORIOS):")
        print("    1. La cámara está encendida y en la misma red WiFi que tu PC.")
        print(f"    2. La IP es correcta? Has introducido: {ip}")
        print("    3. Has creado el 'Usuario' y 'Contraseña' para la Cuenta de cámara DENTRO de la app Tapo?")
        print("       (Tiene que ser un usuario y contraseña que SOLO exista para esto).")
        print("    *****************************************************")