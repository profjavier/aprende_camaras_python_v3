import subprocess
import platform
import re
import ipaddress






def mac_to_ip(subred:str, macs: list) -> dict:

    #subred = "192.168.60.0/24"

    def ping(ip):
        param = "-n" if platform.system().lower() == "windows" else "-c"
        comando = ["ping", param, "1", "-w", "100", str(ip)]
        subprocess.call(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"ping a {ip} ")

    # Hacer ping a toda la red para llenar la tabla ARP
    for ip in ipaddress.IPv4Network(subred):
        ping(ip)

    # Leer tabla ARP del sistema
    arp_output = subprocess.check_output("arp -a", shell=True).decode()

    # Buscar IP y MAC en la salida
    regex = r"(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9:-]{17})"
    matches = re.findall(regex, arp_output)

    mac_ip = {}
    for mac in macs:
        for ip, found_mac in matches:
            if found_mac.lower().replace("-", ":") == mac.lower():
                print(f"IP encontrada: {ip}")
                mac_ip[mac] = ip



    return mac_ip
