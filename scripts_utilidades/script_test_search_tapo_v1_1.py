'''
BUSCA CÁMARAS TAPO POR PROTOCOLO ONVIF

FLUJO GENERAL:
1. Obtiene la IP local del equipo (para inferir la red)
2. Calcula el rango de red (/24)
3. Escanea IPs buscando puertos ONVIF abiertos
4. Intenta conectar por ONVIF
5. Obtiene nombre de la cámara
6. Obtiene MAC desde la interfaz de red ONVIF
7. Compara con el nombre buscado
8. Devuelve la IP encontrada
'''

import socket
import ipaddress
from concurrent.futures import ThreadPoolExecutor

from onvif import ONVIFCamera


USER = "cepy2026"
PASSWORD = "Castelar2026"

# Lista de nombres lógicos que quieres buscar en cámaras
nombre_camaras = ["CASA"]


# ==============================
# OBTENER MACS / INFO DE RED ONVIF
# ==============================
def get_macs(dev):
    """
    Obtiene interfaces de red de la cámara vía ONVIF.
    IMPORTANTE: aquí se obtiene la MAC real del dispositivo.
    """

    interfaces = dev.GetNetworkInterfaces()
    macs = []

    for iface in interfaces:

        # Token interno de la interfaz (eth0, wlan0, etc.)
        print("Nombre interfaz:", iface.token)

        # MAC real del dispositivo
        print("MAC:", iface.Info.HwAddress)

        # Si usa DHCP
        print("DHCP:", iface.IPv4.ConfigApp.DHCP)

        # IP configuradas manualmente (si existen)
        if iface.IPv4.ConfigApp.Manual:
            for ipconf in iface.IPv4.ConfigApp.Manual:
                print("IP:", ipconf.Address)

                # ⚠️ ERROR ORIGINAL: estabas guardando IP como MAC
                # macs.append(ipconf.Address)  ❌ incorrecto

        # ✔️ CORRECTO: guardar MAC real
        macs.append(iface.Info.HwAddress)

    return macs


# =========================
# OBTENER IP LOCAL
# =========================
def obtener_ip_local():
    """
    Detecta la IP local del equipo usando conexión UDP falsa a Internet.
    No envía tráfico real.
    """

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]

    finally:
        s.close()

    return ip


# =========================
# CALCULAR RED LOCAL (/24)
# =========================
def obtener_red():
    """
    Calcula la red local basada en la IP del equipo.
    Ejemplo: 192.168.1.X -> 192.168.1.0/24
    """

    ip_local = obtener_ip_local()

    red = ipaddress.ip_network(ip_local + "/24", strict=False)

    return red


# =========================
# COMPROBAR PUERTO ONVIF
# =========================
def puerto_abierto(ip, port=2020):
    """
    Verifica si el puerto ONVIF está accesible antes de intentar conexión.
    """

    try:
        s = socket.create_connection((str(ip), port), timeout=0.3)
        s.close()
        return True

    except:
        return False


# =========================
# PROBAR CÁMARA POR ONVIF
# =========================
def probar_camara(ip):
    """
    Intenta conectar a una IP como cámara ONVIF.
    Si responde:
      - obtiene hostname
      - obtiene MAC
      - compara nombre lógico
    """

    ip = str(ip)

    # Filtrado rápido por puerto
    if not puerto_abierto(ip):
        return None

    try:
        # Conexión ONVIF directa (NO depende de WS-Discovery)
        cam = ONVIFCamera(
            ip,
            2020,
            USER,
            PASSWORD,
            no_cache=True
        )

        dev = cam.create_devicemgmt_service()

        # Nombre del dispositivo (puede ser genérico en Tapo)
        hostname = dev.GetHostname()
        nombre = hostname.Name

        print(ip, "->", nombre)

        # Comparación con nombre buscado
        if nombre.lower() in [n.lower() for n in nombre_camaras]:

            print(f"✅ ENCONTRADA {ip}")

            return ip

        # Obtener MACs del dispositivo
        macs = get_macs(dev)
        print(f"Lista de MACS de {nombre}:", macs)

    except Exception:
        pass

    return None


# =========================
# MAIN
# =========================
red = obtener_red()

print("Escaneando red:", red)

# Escaneo paralelo para acelerar búsqueda
with ThreadPoolExecutor(max_workers=64) as exe:

    resultados = exe.map(probar_camara, red.hosts())

    for r in resultados:
        if r:
            print("IP FINAL:", r)
            break