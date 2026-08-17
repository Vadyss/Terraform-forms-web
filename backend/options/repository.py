from abc import ABC, abstractmethod

class OptionsRepository(ABC):
    
    @abstractmethod
    async def get_options(self) -> dict:
        ...

class StaticOptionsRepository(OptionsRepository):
    
    async def get_options(self) -> dict:
        return {
            "operatingSystems": [
                {"value": "ubuntu-22.04", "label": "Ubuntu 22.04 LTS"},
                {"value": "debian-12", "label": "Debian 12"},
            ],
            "cpuOptions": [
                {"value": 1, "label": "1 vCPU"},
                {"value": 2, "label": "2 vCPU"},
            ],
            "ramOptions": [
                {"value": 1024, "label": "1 GB"},
                {"value": 2048, "label": "2 GB"},
            ],
            "diskOptions": [
                {"value": 10, "label": "10 GB"},
            ],
            "environmentTypes": [
                {"value": "gui", "label": "GUI"},
                {"value": "cli", "label": "CLI"},
            ],
        }
        
options_repository: OptionsRepository = StaticOptionsRepository()