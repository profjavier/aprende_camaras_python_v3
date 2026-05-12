''' BUSCA CAMARAS TAPO POR PROTOCOLO ONVIF
OBTIENE tambien la mac'''

from onvif import ONVIFCamera
from concurrent.futures import ThreadPoolExecutor

USER = "cepy2026"
PASSWORD = "Castelar2026"

RED = "192.168.1."

nombre_camara="CASA"


def get_macs(dev):
    interfaces = dev.GetNetworkInterfaces()
    macs = []
    for iface in interfaces:

        print("Nombre interfaz:", iface.token)

        print("MAC:", iface.Info.HwAddress)

        print("DHCP:", iface.IPv4.ConfigApp.DHCP)

        if iface.IPv4.ConfigApp.Manual:
            for ipconf in iface.IPv4.ConfigApp.Manual:
                print("IP:", ipconf.Address)
                macs.append(ipconf.Address)
    return macs

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

        macs = get_macs(dev)
        print(f"Lista de MACS de {nombre}", macs)

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