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
import ipaddress
from scapy.all import ARP, Ether, srp
import platform
import socket

# =============================
RED = "192.168.1.0/24"  # Cambia a tu red
# OUIs TP-Link conocidos
MAC_OUI_TPLINK = ["a8:29:48", "60:e3:27", "a4:5e:60", "44:94:fc", "f4:5c:89", "74:83:c2"]
# =============================

print(f"Escaneando red {RED} en busca de TP-Link… Esto puede tardar unos segundos")

# Construir paquete ARP broadcast
packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=RED)
result = srp(packet, timeout=2, verbose=False)[0]

# Filtrar solo TP-Link
for _, received in result:
    mac = received.hwsrc.lower()
    if any(mac.startswith(oui) for oui in MAC_OUI_TPLINK):
        print(f"IP: {received.psrc}  |  MAC: {received.hwsrc}")

