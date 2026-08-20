from proxmox.repository import proxmox_get_vmid
from jobs.repository import job_repository

_TEMPLATE_IDS = {"ubuntu-22.04": 9001, "debian-12": 9000}

async def process_job(job_id: str):
    job = await job_repository.get(job_id)
    if job is None:
        return
    
    vm_config = job.config.virutalMachine
    try:
        template_vmid = _TEMPLATE_IDS[vm_config]
    except KeyError:
        raise ValueError(f"{vm_config} is not a valid value")
    new_vmid = proxmox_get_vmid()