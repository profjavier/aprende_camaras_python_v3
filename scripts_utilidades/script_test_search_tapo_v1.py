''' BUSCA CAMARAS TAPO POR PROTOCOLO ONVIF
PRIMERO OTIENE LA IP ACTUAL DEL EQUIPO UTILIZANDO DNS'''

import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor

from onvif import ONVIFCamera


USER = "cepy2026"
PASSWORD = "Castelar2026"

nombre_camaras = ["CASA"]

# =========================
# OBTENER IP LOCAL
# =========================
def obtener_ip_local():

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]

    finally:
        s.close()

    return ip


# =========================
# CALCULAR RED
# =========================
def obtener_red():

    ip_local = obtener_ip_local()

    # asumimos /24
    red = ipaddress.ip_network(ip_local + "/24", strict=False)

    return red


# =========================
# PUERTO ABIERTO
# =========================
def puerto_abierto(ip, port=2020):

    try:

        s = socket.create_connection(
            (str(ip), port),
            timeout=0.3
        )

        s.close()

        return True

    except:
        return False


# =========================
# PROBAR ONVIF
# =========================
def probar_camara(ip):

    ip = str(ip)

    if not puerto_abierto(ip):
        return None

    try:

        cam = ONVIFCamera(
            ip,
            2020,
            USER,
            PASSWORD,
            no_cache=True
        )

        dev = cam.create_devicemgmt_service()

        hostname = dev.GetHostname()

        nombre = hostname.Name

        print(ip, "->", nombre)

        if nombre.lower() in nombre_camaras:

            print(f"✅ ENCONTRADA {ip}")

            return ip

    except Exception:
        pass

    return None


# =========================
# MAIN
# =========================
red = obtener_red()

print("Escaneando red:", red)

with ThreadPoolExecutor(max_workers=64) as exe:

    resultados = exe.map(probar_camara, red.hosts())

    for r in resultados:

        if r:
            print("IP FINAL:", r)
            break