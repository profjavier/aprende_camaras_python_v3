import cv2
import tkinter as tk
from PIL import Image, ImageTk
from pytapo import Tapo
from datetime import datetime
import os

# ---------------- CONFIGURACIÓN ----------------
# --- CONFIGURACIÓN ---
USUARIO = 'javier'  # El que creaste en la App Tapo
PASSWORD = 'Castelar2026'  # El que creaste en la App Tapo
IP_CAMARA = '192.168.1.200'
PUERTO = '554'  # Puerto RTSP estándar
RTSP_URL = f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAMARA}:{PUERTO}/stream1"

USUARIO = 'cepy2026'  # El que creaste en la App Tapo
PASSWORD = 'Castelar2026'  # El que creaste en la App Tapo
IP_CAMARA = '192.168.60.153'
PUERTO = '554'  # Puerto RTSP estándar
RTSP_URL = f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAMARA}:{PUERTO}/stream1"

# ---------------- CONFIGURACIÓN ----------------

TAPO_IP = f"{IP_CAMARA}"
TAPO_EMAIL = "javier@iescastelar.com"
TAPO_PASSWORD = "Alhambra98"

SAVE_DIR = "../../picar-x/capturas"
VIDEO_SIZE = (400, 300)

PAN_STEP = 10     # grados
TILT_STEP = 10    # grados
# -----------------------------------------------

os.makedirs(SAVE_DIR, exist_ok=True)

# Cámara
cap = cv2.VideoCapture(RTSP_URL)
if not cap.isOpened():
    raise RuntimeError("No se pudo conectar al stream RTSP")

# PTZ
tapo = Tapo(TAPO_IP, TAPO_EMAIL, TAPO_PASSWORD)

root = tk.Tk()
root.title("Tapo C210 PTZ Control")

last_frame = None
fullscreen = False

# ---------------- FUNCIONES VIDEO ----------------

def update_video():
    global last_frame
    ret, frame = cap.read()
    if ret:
        last_frame = frame.copy()
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        img = img.resize(VIDEO_SIZE)
        imgtk = ImageTk.PhotoImage(img)
        video_label.imgtk = imgtk
        video_label.config(image=imgtk)
    root.after(15, update_video)

def capture_photo():
    if last_frame is None:
        return
    img = Image.fromarray(cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGB))
    img = img.resize(VIDEO_SIZE)
    imgtk = ImageTk.PhotoImage(img)
    photo_label.imgtk = imgtk
    photo_label.config(image=imgtk)

def save_photo():
    if last_frame is None:
        return
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"{SAVE_DIR}/foto_{ts}.jpg"
    cv2.imwrite(path, last_frame)
    status.config(text=f"💾 Guardado: {path}")

def toggle_fullscreen():
    global fullscreen
    fullscreen = not fullscreen
    root.attributes("-fullscreen", fullscreen)

def exit_app():
    cap.release()
    root.destroy()

# ---------------- FUNCIONES PTZ ----------------

def move_up():
    #tapo.pan_tilt_relative(0, TILT_STEP)  # sube
    tapo.moveMotor(0,TILT_STEP)  # sube

def move_down():
    tapo.moveMotor(0, -TILT_STEP)  # baja

def move_left():
    tapo.moveMotor(-PAN_STEP, 0)  # izquierda

def move_right():
    tapo.moveMotor(PAN_STEP, 0)   # derecha


def move_to_coords():
    try:
        pan = int(pan_entry.get())
        tilt = int(tilt_entry.get())
        tapo.pan_tilt_to(pan, tilt)
        status.config(text=f"🎯 Moviendo a Pan={pan} Tilt={tilt}")
    except ValueError:
        status.config(text="❌ Coordenadas inválidas")

# ---------------- UI ----------------

video_label = tk.Label(root)
video_label.grid(row=0, column=0, padx=10, pady=10)

photo_label = tk.Label(root)
photo_label.grid(row=0, column=1, padx=10, pady=10)

# ---- Botones foto ----
frame_buttons = tk.Frame(root)
frame_buttons.grid(row=1, column=0, columnspan=2)

tk.Button(frame_buttons, text="📸 Capturar", width=14, command=capture_photo).grid(row=0, column=0, padx=5)
tk.Button(frame_buttons, text="💾 Guardar", width=14, command=save_photo).grid(row=0, column=1, padx=5)
tk.Button(frame_buttons, text="🖥️ Fullscreen", width=14, command=toggle_fullscreen).grid(row=0, column=2, padx=5)
tk.Button(frame_buttons, text="❌ Salir", width=14, command=exit_app).grid(row=0, column=3, padx=5)

# ---- PTZ ----
ptz = tk.Frame(root)
ptz.grid(row=2, column=0, columnspan=2, pady=10)

tk.Button(ptz, text="⬆️", width=6, command=move_up).grid(row=0, column=1)
tk.Button(ptz, text="⬅️", width=6, command=move_left).grid(row=1, column=0)
tk.Button(ptz, text="➡️", width=6, command=move_right).grid(row=1, column=2)
tk.Button(ptz, text="⬇️", width=6, command=move_down).grid(row=2, column=1)

# ---- Coordenadas ----
coords = tk.Frame(root)
coords.grid(row=3, column=0, columnspan=2)

tk.Label(coords, text="Pan:").grid(row=0, column=0)
pan_entry = tk.Entry(coords, width=5)
pan_entry.grid(row=0, column=1)

tk.Label(coords, text="Tilt:").grid(row=0, column=2)
tilt_entry = tk.Entry(coords, width=5)
tilt_entry.grid(row=0, column=3)

tk.Button(coords, text="🎯 Ir a", command=move_to_coords).grid(row=0, column=4, padx=5)

status = tk.Label(root, text="Listo", anchor="w")
status.grid(row=4, column=0, columnspan=2, sticky="w", padx=10)

update_video()
root.mainloop()
