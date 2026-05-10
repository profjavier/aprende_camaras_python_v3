import cv2
import tkinter as tk
from PIL import Image, ImageTk
from datetime import datetime
import os

# ---------------- CONFIGURACIÓN ----------------
# --- CONFIGURACIÓN ---
USUARIO = 'javier'  # El que creaste en la App Tapo
PASSWORD = 'Castelar2026'  # El que creaste en la App Tapo
IP_CAMARA = '192.168.1.200'
PUERTO = '554'  # Puerto RTSP estándar
RTSP_URL = f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAMARA}:{PUERTO}/stream1"

# ---------------- CONFIGURACIÓN ----------------
SAVE_DIR = "../../picar-x/capturas"
VIDEO_SIZE = (400, 300)
# -----------------------------------------------

os.makedirs(SAVE_DIR, exist_ok=True)

cap = cv2.VideoCapture(RTSP_URL)
if not cap.isOpened():
    raise RuntimeError("No se pudo conectar a la cámara")

root = tk.Tk()
root.title("Tapo C210 Control")

fullscreen = False
last_frame = None

# ----------------- FUNCIONES -----------------

def update_video():
    global last_frame

    ret, frame = cap.read()
    if ret:
        last_frame = frame.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb).resize(VIDEO_SIZE)
        imgtk = ImageTk.PhotoImage(img)
        video_label.imgtk = imgtk
        video_label.config(image=imgtk)

    root.after(15, update_video)


def capture_photo():
    if last_frame is None:
        return

    frame_rgb = cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb).resize(VIDEO_SIZE)
    imgtk = ImageTk.PhotoImage(img)
    photo_label.imgtk = imgtk
    photo_label.config(image=imgtk)


def save_photo():
    if last_frame is None:
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SAVE_DIR}/foto_{ts}.jpg"
    cv2.imwrite(filename, last_frame)
    status_label.config(text=f"💾 Guardado: {filename}")


def toggle_fullscreen():
    global fullscreen
    fullscreen = not fullscreen
    root.attributes("-fullscreen", fullscreen)


def exit_app():
    cap.release()
    root.destroy()

# ----------------- UI -----------------

video_label = tk.Label(root)
video_label.grid(row=0, column=0, padx=10, pady=10)

photo_label = tk.Label(root)
photo_label.grid(row=0, column=1, padx=10, pady=10)

buttons_frame = tk.Frame(root)
buttons_frame.grid(row=1, column=0, columnspan=2, pady=10)

tk.Button(buttons_frame, text="🎥 Capturar foto", width=18, command=capture_photo).grid(row=0, column=0, padx=5)
tk.Button(buttons_frame, text="💾 Guardar foto", width=18, command=save_photo).grid(row=0, column=1, padx=5)
tk.Button(buttons_frame, text="🖥️ Pantalla completa", width=18, command=toggle_fullscreen).grid(row=0, column=2, padx=5)
tk.Button(buttons_frame, text="❌ Salir", width=18, command=exit_app).grid(row=0, column=3, padx=5)

status_label = tk.Label(root, text="Listo", anchor="w")
status_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10)

update_video()
root.mainloop()
