import requests
import json

IP_CAMARA = '192.168.1.36'
TAPO_EMAIL = "cepycastelar@gmail.com"
TAPO_PASSWORD = "Castelar2026"

url = f"[{IP_CAMARA}](http://{IP_CAMARA}/stok=login/ds)"
auth_data = {
    "method": "login",
    "params": {
        "username": TAPO_EMAIL,
        "password": TAPO_PASSWORD
    }
}
response = requests.post(url, json=auth_data)
print(response.json())