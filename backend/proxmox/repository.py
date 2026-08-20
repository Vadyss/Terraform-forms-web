import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN_ID = os.getenv("PROXMOX_TOKEN_ID")
TOKEN_SECRET = os.getenv("PROXMOX_TOKEN_SECRET")
PROXMOX_NODE = os.getenv("PROXMOX_NODE")

def proxmox_get_status():
    url = f"https://172.20.10.3:8006/api2/json/nodes/{PROXMOX_NODE}/status"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
        }
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=5)
    except requests.exceptions.RequestException:
        raise ValueError("Timeout after 5s")
    
    return response.json()["data"]

def proxmox_clone(template_vmid, vmid, name):
    url = f"https://172.20.10.3:8006/api2/json/nodes/{PROXMOX_NODE}/qemu/{template_vmid}/clone"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
        }
    try:
        response = requests.post(url, headers=headers, data={"newid": vmid, "name": name, "full": 1}, verify=False, timeout=5)
    except requests.exceptions.RequestException:
        raise ValueError("Timeout after 5s")
    
    return response.json()["data"]

def proxmox_wait_for_task(upid):
    url = f"https://172.20.10.3:8006/api2/json/nodes/{PROXMOX_NODE}/tasks/{upid}/status"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
        }
    try:
        response = requests.post(url, headers=headers, verify=False, timeout=5)
    except requests.exceptions.RequestException:
        raise ValueError("Timeout after 5s")
    
    return response.json()["data"]
    

def proxmox_get_task_status(task_id):
    url = f"https://172.20.10.3:8006/api2/json/nodes/{PROXMOX_NODE}/tasks/{task_id}/status"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
        }
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=5)
    except requests.exceptions.RequestException:
        raise ValueError("Timeout after 5s")
    
    return response.json()["data"]

def proxmox_get_vmid():
    url = "https://172.20.10.3:8006/api2/json/cluster/nextid"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
    }
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=5)
    except requests.exceptions.RequestException:
        raise ValueError("Timeout after 5s")
    
    return response.json()["data"]
