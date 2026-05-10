from scapy.all import ARP, Ether, srp


def mac_to_ip(mac) -> str|None:

    RED = "192.168.60.0/24"
    ip = None
    packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=RED)
    result = srp(packet, timeout=2, verbose=False)[0]

    for _, received in result:
        if received.hwsrc.lower() == mac.lower():
            print(f"IP encontrada: {received.psrc}")
            ip = received.psrc
            break
    else:
        print("MAC no encontrada en la red")
        ip = None
