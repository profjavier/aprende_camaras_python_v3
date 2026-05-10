#!/usr/bin/env python3
"""
Script para controlar cámara Tapo C210
Soporta: ONVIF PTZ, API secreta, y visualización RTSP
"""

"""DEPENDENCIAS
# Primero, actualiza pip
python -m pip install --upgrade pip

# Instala las dependencias principales (evita la que da error)
pip install opencv-python pillow requests numpy

# Instala la versión moderna de ONVIF
pip install onvif-zeep

# Alternativa: si onvif-zeep falla, usa esta opción más simple
pip install zeep
pip install pytapo  # Biblioteca específica para Tapo
"""

import cv2
import numpy as np
import requests
import time
import hashlib
import json
from onvif import ONVIFCamera
from threading import Thread
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk


class TapoC210Controller:
    def __init__(self, ip, username, password, rtsp_user=None, rtsp_pass=None):
        """
        Inicializa el controlador de la cámara Tapo C210

        Args:
            ip: Dirección IP de la cámara
            username: Usuario de la cámara (generalmente "admin")
            password: Contraseña de la cuenta TP-Link
            rtsp_user: Usuario RTSP (opcional, si es diferente)
            rtsp_pass: Contraseña RTSP (opcional)
        """
        self.ip = ip
        self.username = username
        self.password = password
        self.rtsp_user = rtsp_user or username
        self.rtsp_pass = rtsp_pass or password
        self.stok = None
        self.onvif_cam = None

        # URLs base
        self.onvif_url = f"http://{ip}:2020/onvif/device_service"
        self.rtsp_url_high = f"rtsp://{self.rtsp_user}:{self.rtsp_pass}@{ip}:554/stream1"
        self.rtsp_url_low = f"rtsp://{self.rtsp_user}:{self.rtsp_pass}@{ip}:554/stream2"

    def login_api(self):
        """
        Login a la API secreta de Tapo para obtener token
        """
        url = f"http://{self.ip}/"

        # Calcular MD5 de la contraseña (en mayúsculas)
        password_hash = hashlib.md5(self.password.encode()).hexdigest().upper()

        payload = {
            "method": "login",
            "params": {
                "hashed": True,
                "password": password_hash,
                "username": self.username
            }
        }

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "Tapo CameraClient Android",
            "Accept": "application/json",
            "requestByApp": "true"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            data = response.json()

            if data.get("error_code") == 0:
                self.stok = data["result"]["stok"]
                print(f"✓ Login exitoso. STOK: {self.stok}")
                return True
            else:
                print(f"✗ Error de login: {data}")
                return False
        except Exception as e:
            print(f"✗ Error de conexión: {e}")
            return False

    def move_api(self, direction):
        """
        Mueve la cámara usando la API secreta

        Args:
            direction: Dirección (0=izquierda, 90=arriba, 180=derecha, 270=abajo)
        """
        if not self.stok:
            if not self.login_api():
                return False

        url = f"http://{self.ip}/stok={self.stok}/ds"

        payload = {
            "method": "do",
            "motor": {
                "movestep": {
                    "direction": direction
                }
            }
        }

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "User-Agent": "Tapo CameraClient Android"
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=5)
            data = response.json()

            if data.get("error_code") == 0:
                print(f"✓ Movimiento {direction}° exitoso")
                return True
            else:
                print(f"✗ Error en movimiento: {data}")
                return False
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def init_onvif(self):
        """
        Inicializa la conexión ONVIF
        """
        try:
            self.onvif_cam = ONVIFCamera(
                self.ip, 2020, self.rtsp_user, self.rtsp_pass
            )
            # Crear servicio PTZ
            self.ptz_service = self.onvif_cam.create_ptz_service()
            # Obtener perfiles
            media_service = self.onvif_cam.create_media_service()
            self.profiles = media_service.GetProfiles()
            self.profile_token = self.profiles[0].token
            print("✓ ONVIF inicializado correctamente")
            return True
        except Exception as e:
            print(f"✗ Error inicializando ONVIF: {e}")
            print("  Asegúrate de tener instalado python-onvif-zeep")
            return False

    def move_onvif_relative(self, x, y):
        """
        Mueve la cámara relativamente usando ONVIF

        Args:
            x: Movimiento horizontal (-1 a 1)
            y: Movimiento vertical (-1 a 1)
        """
        if not self.onvif_cam:
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
            print(f"✓ Movimiento relativo: x={x}, y={y}")
            return True
        except Exception as e:
            print(f"✗ Error en movimiento ONVIF: {e}")
            return False

    def move_onvif_absolute(self, x, y):
        """
        Mueve la cámara a una posición absoluta usando ONVIF

        Args:
            x: Posición horizontal (-1 a 1)
            y: Posición vertical (-1 a 1)
        """
        if not self.onvif_cam:
            if not self.init_onvif():
                return False

        try:
            request = self.ptz_service.create_type('AbsoluteMove')
            request.ProfileToken = self.profile_token
            request.Position = {
                'PanTilt': {'x': x, 'y': y},
                'Zoom': {'x': 0}
            }
            self.ptz_service.AbsoluteMove(request)
            print(f"✓ Movimiento absoluto: x={x}, y={y}")
            return True
        except Exception as e:
            print(f"✗ Error en movimiento ONVIF: {e}")
            return False

    def get_snapshot(self):
        """
        Captura una imagen de la cámara usando RTSP
        """
        cap = cv2.VideoCapture(self.rtsp_url_low)
        ret, frame = cap.read()
        cap.release()

        if ret:
            # Convertir BGR a RGB para PIL
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            return frame_rgb
        return None

    def start_stream(self, callback):
        """
        Inicia el stream de video en un hilo separado

        Args:
            callback: Función que recibe cada frame
        """

        def stream_thread():
            cap = cv2.VideoCapture(self.rtsp_url_low)

            while self.streaming:
                ret, frame = cap.read()
                if ret:
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    callback(frame_rgb)
                else:
                    break

            cap.release()

        self.streaming = True
        self.thread = Thread(target=stream_thread, daemon=True)
        self.thread.start()

    def stop_stream(self):
        """
        Detiene el stream de video
        """
        self.streaming = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1)


class TapoGUI:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Control Tapo C210")
        self.root.geometry("800x600")

        # Frame de video
        self.video_frame = ttk.Frame(self.root)
        self.video_frame.pack(pady=10)

        self.video_label = ttk.Label(self.video_frame)
        self.video_label.pack()

        # Frame de controles
        self.controls_frame = ttk.Frame(self.root)
        self.controls_frame.pack(pady=10)

        # Botones de dirección
        btn_style = {"width": 8, "height": 2}

        self.btn_up = ttk.Button(
            self.controls_frame, text="▲",
            command=lambda: self.move(0, -0.2),
            **btn_style
        )
        self.btn_up.grid(row=0, column=1, padx=5, pady=5)

        self.btn_left = ttk.Button(
            self.controls_frame, text="◄",
            command=lambda: self.move(-0.2, 0),
            **btn_style
        )
        self.btn_left.grid(row=1, column=0, padx=5, pady=5)

        self.btn_stop = ttk.Button(
            self.controls_frame, text="■",
            command=self.stop,
            **btn_style
        )
        self.btn_stop.grid(row=1, column=1, padx=5, pady=5)

        self.btn_right = ttk.Button(
            self.controls_frame, text="►",
            command=lambda: self.move(0.2, 0),
            **btn_style
        )
        self.btn_right.grid(row=1, column=2, padx=5, pady=5)

        self.btn_down = ttk.Button(
            self.controls_frame, text="▼",
            command=lambda: self.move(0, 0.2),
            **btn_style
        )
        self.btn_down.grid(row=2, column=1, padx=5, pady=5)

        # Botones de preset
        preset_frame = ttk.Frame(self.root)
        preset_frame.pack(pady=10)

        ttk.Button(
            preset_frame, text="Home",
            command=lambda: self.move_absolute(-0.4, 0.2)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            preset_frame, text="Esquina",
            command=lambda: self.move_absolute(0.5, -0.5)
        ).pack(side=tk.LEFT, padx=5)

        # Selector de método
        method_frame = ttk.Frame(self.root)
        method_frame.pack(pady=10)

        ttk.Label(method_frame, text="Método de control:").pack(side=tk.LEFT)
        self.method_var = tk.StringVar(value="onvif")
        ttk.Radiobutton(
            method_frame, text="ONVIF", variable=self.method_var, value="onvif"
        ).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(
            method_frame, text="API Secreta", variable=self.method_var, value="api"
        ).pack(side=tk.LEFT, padx=5)

        # Estado
        self.status_label = ttk.Label(self.root, text="Conectando...")
        self.status_label.pack(pady=10)

        # Iniciar stream
        self.controller.start_stream(self.update_video)

    def move(self, dx, dy):
        """Mueve la cámara relativamente"""
        if self.method_var.get() == "onvif":
            self.controller.move_onvif_relative(dx, dy)
        else:
            # Convertir coordenadas a direcciones de API
            if dx > 0:
                self.controller.move_api(180)  # Derecha
            elif dx < 0:
                self.controller.move_api(0)  # Izquierda
            elif dy > 0:
                self.controller.move_api(270)  # Abajo
            elif dy < 0:
                self.controller.move_api(90)  # Arriba

        self.status_label.config(text=f"Movimiento: dx={dx}, dy={dy}")

    def move_absolute(self, x, y):
        """Mueve a posición absoluta"""
        self.controller.move_onvif_absolute(x, y)
        self.status_label.config(text=f"Posición absoluta: x={x}, y={y}")

    def stop(self):
        """Detiene el movimiento actual"""
        self.controller.move_onvif_relative(0, 0)
        self.status_label.config(text="Movimiento detenido")

    def update_video(self, frame):
        """Actualiza el frame de video en la GUI"""
        # Redimensionar para la GUI
        height, width = frame.shape[:2]
        if width > 640:
            scale = 640 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            frame = cv2.resize(frame, (new_width, new_height))

        # Convertir a PhotoImage
        image = Image.fromarray(frame)
        photo = ImageTk.PhotoImage(image=image)

        self.video_label.config(image=photo)
        self.video_label.image = photo

    def run(self):
        """Ejecuta la GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Limpia recursos al cerrar"""
        self.controller.stop_stream()
        self.root.destroy()


def main():
    """
    Configuración principal
    """
    print("=== Controlador para Tapo C210 ===\n")

    # Configuración - ¡CAMBIAR ESTOS VALORES!
    ip = input("IP de la cámara (ej: 192.168.1.100): ").strip()
    username = input("Usuario (generalmente 'admin'): ").strip() or "admin"
    password = input("Contraseña de la cuenta TP-Link: ").strip()

    print("\n[*] Conectando a la cámara...")

    # Crear controlador
    controller = TapoC210Controller(ip, username, password)

    # Probar conexión
    if controller.login_api():
        print("[✓] Conexión API exitosa")
    else:
        print("[!] No se pudo conectar por API, el control ONVIF puede funcionar igual")

    # Iniciar GUI
    gui = TapoGUI(controller)
    gui.run()


if __name__ == "__main__":
    main()