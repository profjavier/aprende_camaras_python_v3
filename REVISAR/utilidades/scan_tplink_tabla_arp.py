'''
Filtrar por fabricante usando MAC
Los fabricantes se identifican por los primeros 3 bytes de la MAC, llamados OUI (Organizationally Unique Identifier). Para TP-Link, los más comunes son:
60:e3:27
a4:5e:60
44:94:fc
f4:5c:89
74:83:c2
A8:29:48
⚠️ TP-Link tiene varios OUIs según modelo y país, así que puedes añadir más si conoces otros.
'''

# filtrar_tp_link.py
import subprocess
import re

# Lista de OUI TP-Link más comunes (agregar si quieres más)
# OUI de TP-Link que conocemos (agrega más si tienes otros dispositivos)
MAC_OUI_TPLINK = ["a8:29:48", "60:e3:27", "a4:5e:60", "44:94:fc", "f4:5c:89", "74:83:c2"]


# Obtener tabla ARP del sistema
output = subprocess.check_output("arp -a", shell=True).decode()

print("Cámaras TP-Link detectadas:")

for line in output.splitlines():
    # Buscar IP y MAC
    match = re.search(r"\(([\d.]+)\).*?([0-9a-f:]{17})", line, re.I)
    if match:
        ip, mac = match.groups()
        mac_lower = mac.lower()
        # Comprobar si MAC empieza con alguno de los OUI de TP-Link
        if any(mac_lower.startswith(oui) for oui in MAC_OUI_TPLINK):
            print(f"IP: {ip}  |  MAC: {mac}")
