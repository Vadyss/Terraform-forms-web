from proxmox.repository import proxmox_get_vmid
from proxmox.repository import proxmox_clone
from proxmox.repository import proxmox_wait_for_task
from proxmox.repository import proxmox_set_options
from proxmox.repository import proxmox_set_disk
from jobs.repository import job_repository

_TEMPLATE_IDS = {"debian-12": 9000, "ubuntu-22.04": 9001}
_TEMPLATE_DISK_SIZES = {"debian-12": 3, "ubuntu-22.04": 3.5}
ciuser = "admin"

async def process_job(job_id: str):
    job = await job_repository.get(job_id)
    if job is None:
        return
    
    vm_config = job.config.virtualMachine
    try:
        template_vmid = _TEMPLATE_IDS[vm_config.os]
        template_disk = _TEMPLATE_DISK_SIZES[vm_config.os]
    except KeyError:
        raise ValueError(f"{vm_config.os} is not a valid value")
    new_vmid = proxmox_get_vmid()
    
    upid = proxmox_clone(template_vmid,new_vmid,vm_config.name)
    
    proxmox_wait_for_task(upid)
    
    proxmox_set_options(new_vmid, vm_config.cpu, vm_config.ram, vm_config.sshkey, ciuser)
    
    try:
        if vm_config.disk > template_disk:
            proxmox_set_disk(new_vmid, template_disk, vm_config.disk)
    except ValueError as e:
        print(f"Disk error: {e}")
    
    # TODO krok 11: start
    # TODO krok 12: wait for start task
    # TODO krok 13: update job status (done/error)