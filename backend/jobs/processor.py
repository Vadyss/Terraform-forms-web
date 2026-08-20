from proxmox.repository import proxmox_get_vmid
from proxmox.repository import proxmox_clone
from jobs.repository import job_repository

_TEMPLATE_IDS = {"debian-12": 9000, "ubuntu-22.04": 9001}

async def process_job(job_id: str):
    job = await job_repository.get(job_id)
    if job is None:
        return
    
    vm_config = job.config.virtualMachine
    try:
        template_vmid = _TEMPLATE_IDS[vm_config.os]
    except KeyError:
        raise ValueError(f"{vm_config.os} is not a valid value")
    new_vmid = proxmox_get_vmid()
    
    upid = proxmox_clone(template_vmid,new_vmid,vm_config.name)
    
    # TODO krok 9: wait for clone task
    # TODO krok 10: configure CPU/RAM/disk/cloud-init
    # TODO krok 11: start
    # TODO krok 12: wait for start task
    # TODO krok 13: update job status (done/error)