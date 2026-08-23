import os
import requests
from dotenv import load_dotenv

import time

load_dotenv()
TOKEN_ID = os.getenv("PROXMOX_TOKEN_ID")
TOKEN_SECRET = os.getenv("PROXMOX_TOKEN_SECRET")
PROXMOX_NODE = os.getenv("PROXMOX_NODE")

max_attempts = 120

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
    attempts = 0
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
        }
    
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=5)
        attempts += 1
        time.sleep(2)
    except requests.exceptions.RequestException:
        raise ValueError("Timeout after 5s")
    
    while response.json()["data"]["status"] == "running" and max_attempts >= attempts:
        try:
            response = requests.get(url, headers=headers, verify=False, timeout=5)
            attempts += 1
            time.sleep(2)
        except requests.exceptions.RequestException:
            raise ValueError("Timeout after 5s")
        
    if response.json()["data"]["exitstatus"] == "OK":
        return response.json()["data"]["exitstatus"]
    else:
        raise ValueError("Template cloning failed.")

def proxmox_set_options(new_vmid, cores, memory, sshkey, ciuser):
    url = f"https://172.20.10.3:8006/api2/json/nodes/{PROXMOX_NODE}/qemu/{new_vmid}/config"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
        }
    try:
        response = requests.post(url, headers=headers, data={"cores": cores, "memory": memory, "sshkey": sshkey, "ciuser": ciuser}, verify=False, timeout=5)
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