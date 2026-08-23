from proxmox.repository import proxmox_get_vmid
from proxmox.repository import proxmox_clone
from proxmox.repository import proxmox_wait_for_task
from proxmox.repository import proxmox_set_options
from jobs.repository import job_repository

_TEMPLATE_IDS = {"debian-12": 9000, "ubuntu-22.04": 9001}
ciuser = "admin"

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
    print(f"UPID: {upid}")
    
    proxmox_wait_for_task(upid)
    
    proxmox_set_options(new_vmid, vm_config.cpu, vm_config.ram, vm_config.sshkey, ciuser)
    # TODO krok 11: start
    # TODO krok 12: wait for start task
    # TODO krok 13: update job status (done/error)