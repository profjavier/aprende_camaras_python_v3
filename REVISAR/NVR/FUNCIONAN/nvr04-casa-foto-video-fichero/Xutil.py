import subprocess
import platform
import re
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed

'''
Laza pings paralelos
'''

def mac_to_ip(subred: str, macs: list) -> dict:

    def ping(ip):
        param = "-n" if platform.system().lower() == "windows" else "-c"
        comando = ["ping", param, "1", "-w", "100", str(ip)]
        subprocess.call(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return str(ip)

    # Hacer ping en paralelo
    ips = list(ipaddress.IPv4Network(subred))
    with ThreadPoolExecutor(max_workers=50) as executor:  # ajustar workers según CPU/red
        futures = [executor.submit(ping, ip) for ip in ips]
        for _ in as_completed(futures):
            pass  # solo esperamos que terminen

    # Leer tabla ARP
    # Codificacion UTF-8
    '''arp_output = subprocess.check_output("arp -a", shell=True).decode()'''
    # Codificacion dinámica del sistema
    '''
    import locale
    encoding = locale.getpreferredencoding()
    arp_output = subprocess.check_output("arp -a", shell=True).decode(encoding)
    '''
    # Codificacion windows
    arp_output = subprocess.check_output("arp -a", shell=True).decode("cp1252")

    regex = r"(\d+\.\d+\.\d+\.\d+)\s+([a-fA-F0-9:-]{17})"
    matches = re.findall(regex, arp_output)

    mac_ip = {}
    macs_normalizadas = [m.lower().replace("-", ":") for m in macs]

    for ip_addr, found_mac in matches:
        print(ip_addr, found_mac)
        '''if ip_addr == "192.168.60.188":
            pass'''
        found_mac_norm = found_mac.lower().replace("-", ":")
        if found_mac_norm in macs_normalizadas:
            mac_ip[found_mac_norm] = ip_addr
            print(f"IP encontrada: {ip_addr} para MAC {found_mac_norm}")

    return mac_ip
