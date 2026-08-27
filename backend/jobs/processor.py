from proxmox.repository import proxmox_get_vmid
from proxmox.repository import proxmox_clone
from proxmox.repository import proxmox_wait_for_task
from proxmox.repository import proxmox_set_options
from proxmox.repository import proxmox_set_disk
from proxmox.repository import proxmox_start
from proxmox.repository import proxmox_wait_for_ip
from jobs.store import JobOutputs
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
    
    try:
        new_vmid = proxmox_get_vmid()
        
        upid = proxmox_clone(template_vmid,new_vmid,vm_config.name)
        
        proxmox_wait_for_task(upid)
        
        proxmox_set_options(new_vmid, vm_config.cpu, vm_config.ram, vm_config.sshkey, ciuser)
        
        try:
            if vm_config.disk > template_disk:
                proxmox_set_disk(new_vmid, template_disk, vm_config.disk)
        except ValueError as e:
            print(f"Disk error: {e}")
            
        start_upid = proxmox_start(new_vmid)
        proxmox_wait_for_task(start_upid)
        
        ip = proxmox_wait_for_ip(new_vmid)
        await job_repository.update(job_id, status="done", outputs=JobOutputs(ip=ip, resourceId=str(new_vmid)))
    except ValueError as e:
        await job_repository.update(job_id, status="error", error=str(e))
        return
    await job_repository.update(job_id, status="done")