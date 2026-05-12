''' BUSCA CAMARAS TAPO POR PROTOCOLO ONVIF '''

from onvif import ONVIFCamera
from concurrent.futures import ThreadPoolExecutor

USER = "cepy2026"
PASSWORD = "Castelar2026"

RED = "192.168.1."

nombre_camara="CASA"

def probar_ip(ip):

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

        if nombre_camara in nombre.lower():
            print(f"✅ ENCONTRADA: {ip}")

            return ip

    except:
        pass

    return None


ips = [RED + str(i) for i in range(1, 255)]

with ThreadPoolExecutor(max_workers=50) as exe:

    resultados = exe.map(probar_ip, ips)

    for r in resultados:
        if r:
            print("IP FINAL:", r)
            break