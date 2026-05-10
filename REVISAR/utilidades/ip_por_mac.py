from scapy.all import ARP, Ether, srp

MAC_OBJETIVO = "84:7b:57:b1:c1:14"
MAC_OBJETIVO = "EC:75:0C:12:2F:83"
RED = "192.168.1.0/24"

packet = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=RED)
result = srp(packet, timeout=2, verbose=False)[0]

for _, received in result:
    if received.hwsrc.lower() == MAC_OBJETIVO.lower():
        print(f"IP encontrada: {received.psrc}")
        break
else:
    print("MAC no encontrada en la red")


'''IP: 192.168.1.1  |  MAC: 62:f:e1:4a:92:
IP: 192.168.1.104  |  MAC: 6e:88:e4:a:cf:
IP: 192.168.1.113  |  MAC: ae:29:48:5d:2d:23
IP: 192.168.1.175  |  MAC: 0:7c:2d:84:ea:
IP: 192.168.1.177  |  MAC: 36:aa:f8:86:2f
IP: 192.168.1.178  |  MAC: 84:7b:57:b1:c1:14
IP: 192.168.1.179  |  MAC: ae:29:48:5d:2d:23
IP: 192.168.1.255  |  MAC: ff:ff:ff:ff:ff:ff
IP: 239.255.255.250  |  MAC: 1:0:5e:7f:ff:f0'''