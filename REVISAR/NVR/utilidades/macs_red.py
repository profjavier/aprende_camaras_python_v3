import subprocess
import re
import platform
import ipaddress
import os
import threading

# ===============================
RED = "192.168.1.0/24"
PING_THREADS = 50
TIMEOUT = 1000
# ===============================

def ping(ip):
    param = "-n" if platform.system().lower() == "windows" else "-c"
    timeout_param = "-w" if platform.system().lower() == "windows" else "-W"
    try:
        with open(os.devnull, "w") as DEVNULL:
            subprocess.run(
                ["ping", param, "1", timeout_param, str(int(TIMEOUT/1000)), str(ip)],
                stdout=DEVNULL, stderr=DEVNULL
            )
    except Exception:
        pass

def scan_red(red):
    threads = []
    for ip in ipaddress.ip_network(red).hosts():
        t = threading.Thread(target=ping, args=(ip,))
        threads.append(t)
        t.start()
        while threading.active_count() > PING_THREADS:
            pass
    for t in threads:
        t.join()

def obtener_tabla_arp():
    system = platform.system().lower()
    if system == "windows":
        comando = "arp -a"
    elif system == "darwin":  # macOS
        comando = "arp -a"
    else:  # Linux
        comando = "ip neigh"

    output = subprocess.check_output(comando, shell=True).decode()

    resultado = []
    if system in ["windows", "darwin"]:
        # IP y MAC estilo arp -a
        for linea in output.splitlines():
            match = re.search(r"\(([\d.]+)\).*?([0-9a-f:]{17}|[0-9a-f:]{14}|[0-9a-f]{2}(?:-[0-9a-f]{2}){5})", linea, re.I)
            if match:
                ip, mac = match.groups()
                mac = mac.replace("-", ":").lower()
                resultado.append((ip, mac))
    else:  # Linux ip neigh
        for linea in output.splitlines():
            parts = linea.split()
            if len(parts) >= 5 and parts[4].count(":") == 5:
                resultado.append((parts[0], parts[4].lower()))

    return resultado

# ===============================
if __name__ == "__main__":
    print(f"Escaneando red {RED}… Esto puede tardar unos segundos")
    scan_red(RED)
    print("\nEquipos detectados:\n")
    for ip, mac in obtener_tabla_arp():
        print(f"IP: {ip}  |  MAC: {mac}")
