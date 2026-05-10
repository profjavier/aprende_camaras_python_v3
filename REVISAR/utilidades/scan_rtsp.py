'''
Detectar RTSP activos
Este script intenta conectarse al puerto 554 (RTSP) y verifica si responde con el protocolo.
'''

# rtsp_activos.py
import socket

IPS_CAMARAS = ["192.168.1.101", "192.168.1.102"]  # Reemplaza con las IPs detectadas
RTSP_PORT = 554

for ip in IPS_CAMARAS:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        sock.connect((ip, RTSP_PORT))
        sock.send(b"OPTIONS rtsp://"+ip.encode()+b"/ RTSP/1.0\r\nCSeq: 1\r\n\r\n")
        data = sock.recv(1024)
        sock.close()
        if b"RTSP" in data:
            print(f"RTSP activo en {ip}")
    except Exception:
        pass
