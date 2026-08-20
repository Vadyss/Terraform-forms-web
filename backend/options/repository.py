from abc import ABC, abstractmethod

from proxmox.repository import proxmox_get_status

class OptionsRepository(ABC):
    
    @abstractmethod
    async def get_options(self) -> dict:
        ...

class StaticOptionsRepository(OptionsRepository):

    async def get_options(self) -> dict:
        status = proxmox_get_status()
        max_ram = status["memory"]["available"] // (1024 ** 2)   # v MB
        max_cpu = status["cpuinfo"]["cpus"]
        max_disk = status["rootfs"]["avail"] // (1024 ** 3)      # v GB
        
        all_cpu_options = [
            {"value": v, "label": f"{v} vCPU"} for v in range(1, 12)
        ]

        all_ram_options = [
            {"value": v * 1024, "label": f"{v} GB"} for v in range(1, 128)
        ]

        all_disk_options = [
            {"value": v, "label": f"{v} GB"} for v in range(10, 501, 10)
        ]

        return {
            "operatingSystems": [
                {"value": "ubuntu-22.04", "label": "Ubuntu 22.04 LTS"},
                {"value": "debian-12", "label": "Debian 12"},
            ],
            "cpuOptions": [o for o in all_cpu_options if o["value"] <= max_cpu],
            "ramOptions": [o for o in all_ram_options if o["value"] <= max_ram],
            "diskOptions": [o for o in all_disk_options if o["value"] <= max_disk],
            "environmentTypes": [
                {"value": "gui", "label": "GUI"},
                {"value": "cli", "label": "CLI"},
            ],
        }
        
options_repository: OptionsRepository = StaticOptionsRepository()