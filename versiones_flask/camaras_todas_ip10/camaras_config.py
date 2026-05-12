'''
pip install scapy
'''
import os

from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import srp


class CamarasConfig:

    def __init__(self, app, ruta):
        self.app_flask = app
        self.ruta = ruta
        self.camaras_activas = []
        self.subred = None
        self.cargar_camaras()


    # -------------------------
    # CONFIG CAMARAS
    # -------------------------
    def cargar_camaras(self):

        camaras = []

        self.app_flask.logger.info(f"Cargando cámaras desde {self.ruta}")

        try:
            ruta_config_lan = os.path.join(self.ruta, "config_lan.cfg")
            ruta_config_camaras = os.path.join(self.ruta, "config_camaras.cfg")
            # print("RUTA BASE:", self.ruta)
            # print("LAN:", ruta_config_lan)
            # print("CAMARAS:", ruta_config_camaras)
            with open(ruta_config_lan, "r") as f:
                self.subred = f.readline().strip()

            with open(ruta_config_camaras, "r") as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea:
                        continue

                    id_cam, mac, port, user, password = linea.split(":")

                    camaras.append({
                        "id": id_cam,
                        "mac": mac,
                        "port": int(port),
                        "user": user,
                        "password": password
                    })
            self.buscar_mac_en_red(camaras)
            self.app_flask.logger.info("Cámaras cargadas")

        except Exception:
            self.app_flask.logger.exception("Error cargando cámaras")


    # -------------------------
    # Busca MAC
    # -------------------------
    def buscar_mac_en_red(self, camaras):
        self.camaras_activas = []

        arp = ARP(pdst=self.subred)
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")

        paquete = ether / arp

        respuestas = srp(paquete, timeout=2, verbose=0)[0]

        for _, recibido in respuestas:

            mac = recibido.hwsrc.replace(":", "-")
            ip = recibido.psrc

            # print(ip, mac)
            for camara in camaras:
                if camara["mac"].lower() == mac.lower():
                    camara["ip"] = ip
                    self.camaras_activas.append(camara)
                    break
