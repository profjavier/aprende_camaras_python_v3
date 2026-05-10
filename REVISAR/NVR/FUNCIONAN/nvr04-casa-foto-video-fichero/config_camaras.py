import ipaddress
import platform
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


class ConfigCamaras:
    SUBRED = "192.168.60.0/24"

    def __init__(self, pathname='config_camaras.cfg'):
        self.pathname = pathname
        self.camaras = []

    def cargar_camaras_config(self):
        self.camaras = []

        with open(self.pathname, "r") as f:
            for linea in f:
                linea = linea.strip()

                if not linea:
                    continue  # saltar líneas vacías

                partes = linea.split(":")

                if len(partes) != 6:
                    print(f"Línea inválida: {linea}")
                    continue

                id, ip, mac, port, user, password = partes

                camara = {
                    "id": id,
                    "ip": ip,
                    "mac": mac,
                    "port": int(port),
                    "user": user,
                    "password": password
                }

                self.camaras.append(camara)

        self.comprobar_camaras()

        return self.camaras_activas_config



    def comprobar_camaras(self):
        # Obtener todas las MACs
        macs = [camara["mac"] for camara in self.camaras]
        macs_to_ip = self.mac_to_ip(self.SUBRED, macs)

        self.camaras_activas_config = []
        for camara_cfg in self.camaras:
            if macs_to_ip.get(camara_cfg['mac'].lower().replace("-", ":"), None):
                camara_cfg["ip"] = macs_to_ip.get(camara_cfg['mac'].lower().replace("-", ":"))
                self.camaras_activas_config.append(camara_cfg)
        return self.camaras_activas_config
    '''
    Laza pings paralelos
    '''
    def mac_to_ip(self, subred: str, macs: list) -> dict:

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
