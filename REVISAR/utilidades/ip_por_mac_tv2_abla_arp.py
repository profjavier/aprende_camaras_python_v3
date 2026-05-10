import subprocess
import re

MAC_OBJETIVO = "62:f:e1:4a:92:9e"

output = subprocess.check_output("arp -a", shell=True).decode()

for line in output.splitlines():
    if MAC_OBJETIVO.lower() in line.lower():
        print("IP encontrada:", line)
        break
else:
    print("MAC no encontrada")
