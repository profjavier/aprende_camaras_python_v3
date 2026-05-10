from ping3 import ping
import ipaddress

red = ipaddress.ip_network("192.168.1.0/24", strict=False)

print("Escaneando red...\n")

GREEN = "\033[92m"
RED = "\033[31m"


for ip in red.hosts():
    respuesta = ping(str(ip), timeout=1)
    if respuesta:
        print(f"\r{GREEN}[✔] IP activa: {ip}")
    else:
        print(f"\r{RED}Analizando: {ip}", end="", flush=True)

