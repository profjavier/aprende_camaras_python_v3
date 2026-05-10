import cv2
import tkinter as tk
from PIL import Image, ImageTk
from pytapo import Tapo
from datetime import datetime
import os


import subprocess

# Prueba si la cámara responde
response = subprocess.run(['ping', '-n', '1', '192.168.1.36'], capture_output=True)
print("Cámara accesible:", response.returncode == 0)

from pytapo import Tapo

IP_CAMARA = '192.168.1.36'
TAPO_EMAIL = "cepycastelar@gmail.com"
TAPO_PASSWORD = "Castelar2026"
# try:
#     tapo = Tapo(IP_CAMARA, TAPO_EMAIL, TAPO_PASSWORD)
#
#     print(tapo.getBasicInfo())
# except Exception as err:
#     print(err)
tapo = Tapo(IP_CAMARA, TAPO_EMAIL, TAPO_PASSWORD)

print(tapo.getBasicInfo())