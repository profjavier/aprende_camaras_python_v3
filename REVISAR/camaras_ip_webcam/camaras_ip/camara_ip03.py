import cv2
import tkinter as tk
from PIL import Image, ImageTk

# ---------------- CONFIGURACIÓN ----------------
# --- CONFIGURACIÓN ---
USUARIO = 'javier'  # El que creaste en la App Tapo
PASSWORD = 'Castelar2026'  # El que creaste en la App Tapo
IP_CAMARA = '192.168.1.200'
PUERTO = '554'  # Puerto RTSP estándar
RTSP_URL = f"rtsp://{USUARIO}:{PASSWORD}@{IP_CAMARA}:{PUERTO}/stream1"
# -----------------------------------------------

cap = cv2.VideoCapture(RTSP_URL)

if not cap.isOpened():
    raise RuntimeError("No se pudo conectar a la cámara")

# ---------- Ventana ----------
root = tk.Tk()
root.title("Tapo C210")

video_label = tk.Label(root)
video_label.grid(row=0, column=0, padx=10, pady=10)

photo_label = tk.Label(root)
photo_label.grid(row=0, column=1, padx=10, pady=10)

last_frame = None


def update_video():
    global last_frame

    ret, frame = cap.read()
    if ret:
        last_frame = frame.copy()

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        img = img.resize((400, 300))

        imgtk = ImageTk.PhotoImage(image=img)
        video_label.imgtk = imgtk
        video_label.configure(image=imgtk)

    root.after(10, update_video)


def capture_photo():
    if last_frame is None:
        return

    frame_rgb = cv2.cvtColor(last_frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    img = img.resize((400, 300))

    imgtk = ImageTk.PhotoImage(image=img)
    photo_label.imgtk = imgtk
    photo_label.configure(image=imgtk)


# ---------- Botón ----------
btn = tk.Button(root, text="📸 Capturar foto", command=capture_photo, width=20)
btn.grid(row=1, column=0, columnspan=2, pady=10)

update_video()
root.mainloop()

cap.release()
