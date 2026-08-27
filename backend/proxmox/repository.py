import os
import requests
from dotenv import load_dotenv

import time
from urllib.parse import quote

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

def proxmox_set_options(vmid, cores, memory, sshkeys, ciuser):
    url = f"https://172.20.10.3:8006/api2/json/nodes/{PROXMOX_NODE}/qemu/{vmid}/config"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
        }
    try:
        response = requests.post(url, headers=headers, data={"cores": cores, "memory": memory, "sshkeys": quote(sshkeys, safe=""), "ciuser": ciuser}, verify=False, timeout=5)
        if response.status_code != 200:
            raise ValueError(f"Proxmox config failed: {response.status_code} {response.text}")
    except requests.exceptions.RequestException:
        raise ValueError("Timeout after 5s")
    
    return response.json()["data"]

def proxmox_set_disk(vmid, disk_size, new_disk_size):
    url = f"https://172.20.10.3:8006/api2/json/nodes/{PROXMOX_NODE}/qemu/{vmid}/resize"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
        }
    
    set_disk_size = new_disk_size - disk_size
    
    if set_disk_size > 0:
        set_disk_size = "+" + f"{set_disk_size}" + "G"
    else:
        set_disk_size = f"{set_disk_size}" + "G"
    
    try:
        response = requests.put(url, headers=headers, data={"disk": "scsi0", "size": set_disk_size}, verify=False, timeout=5)
        if response.status_code != 200:
            raise ValueError(f"Proxmox config failed: {response.status_code} {response.text}")
    except requests.exceptions.RequestException:
        raise ValueError("Timeout after 5s")
    
    return response.json()["data"]

def proxmox_start(vmid):
    url = f"https://172.20.10.3:8006/api2/json/nodes/{PROXMOX_NODE}/qemu/{vmid}/status/start"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
        }
    try:
        response = requests.post(url, headers=headers, verify=False, timeout=5)
        if response.status_code != 200:
            raise ValueError(f"Proxmox config failed: {response.status_code} {response.text}")
    except requests.exceptions.RequestException:
        raise ValueError("Timeout after 5s")
    
    return response.json()["data"]

def proxmox_get_ip(vmid):
    url = f"https://172.20.10.3:8006/api2/json/nodes/{PROXMOX_NODE}/qemu/{vmid}/agent/network-get-interfaces"
    headers = {
        "Authorization": f"PVEAPIToken={TOKEN_ID}={TOKEN_SECRET}"
        }
    try:
        response = requests.get(url, headers=headers, verify=False, timeout=5)
        print(response.status_code)
    except requests.exceptions.RequestException:
        raise ValueError("Timeout after 5s")
    
    data = response.json()["data"]["result"]
    
    for interface in data:
        if interface["name"] != "lo":
            for ip in interface["ip-addresses"]:
                if ip["ip-address-type"] == "ipv4":
                    return ip["ip-address"]

def proxmox_wait_for_ip(vmid):
    attempts = 0
    while attempts < max_attempts:
        try:
            ip = proxmox_get_ip(vmid)
            if ip:
                return ip
        except ValueError:
            pass
        attempts += 1
        time.sleep(15)
    raise ValueError("Could not get VM IP after multiple attempts")

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