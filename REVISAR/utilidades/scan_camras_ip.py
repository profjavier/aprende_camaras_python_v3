'''
Escaneo de red y detección de cámaras IP
Este script hace ping a todas las IPs de tu red y consulta la tabla ARP para obtener IP + MAC.
Filtraremos por puertos típicos de cámaras (80, 554, 8000) para identificar dispositivos tipo cámara.
'''

# camaras_red.py
import ipaddress
import subprocess
import threading
import socket

RED = "192.168.1.0/24"
PING_THREADS = 50
CAM_PORTS = [80, 554, 8000]  # Puertos típicos de cámaras

# =========================
# Hacer ping
def ping(ip):
    param = "-n" if subprocess.os.name == "nt" else "-c"
    timeout_param = "-w" if subprocess.os.name == "nt" else "-W"
    try:
        subprocess.run(
            ["ping", param, "1", timeout_param, "1", str(ip)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

def scan_red(red):
    threads = []
    for ip in ipaddress.ip_network(red).hosts():
        t = threading.Thread(target=ping, args=(ip,))
        threads.append(t)
        t.start()
        while threading.active_count() > PING_THREADS:
            pass
    for t in threads:
        t.join()

# =========================
# Revisar si el host tiene puertos típicos de cámara abiertos
def is_camara(ip):
    for port in CAM_PORTS:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((str(ip), port))
            sock.close()
            return True
        except:
            continue
    return False

# =========================
# Ejecutar
if __name__ == "__main__":
    print("Escaneando red...")
    scan_red(RED)

    print("\nCámaras detectadas:")
    for ip in ipaddress.ip_network(RED).hosts():
        if is_camara(ip):
            print(ip)
