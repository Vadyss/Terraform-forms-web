import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN_ID = os.getenv("PROXMOX_TOKEN_ID")
TOKEN_SECRET = os.getenv("PROXMOX_TOKEN_SECRET")
PROXMOX_NODE = os.getenv("PROXMOX_NODE")

def proxmox_get_status():
    url = f"https://192.168.16.201:8006/api2/json/nodes/{PROXMOX_NODE}/status"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
        }
    response = requests.get(url, headers=headers, verify=False)
    
    return response.json()["data"]

def proxmox_get_vmid():
    url = "https://192.168.16.201:8006/api2/json/cluster/nextid"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
    }
    response = requests.get(url, headers=headers, verify=False)
    data_json = response.json()
    
    return data_json["data"]