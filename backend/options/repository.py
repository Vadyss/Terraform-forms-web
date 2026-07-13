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
                {"value": "windows-2022", "label": "Windows Server 2022"},
            ],
            "cpuOptions": [
                {"value": 1, "label": "1 vCPU"},
                {"value": 2, "label": "2 vCPU"},
                {"value": 3, "label": "3 vCPU"},
                {"value": 4, "label": "4 vCPU"},
                {"value": 5, "label": "5 vCPU"},
                {"value": 6, "label": "6 vCPU"},
                {"value": 7, "label": "7 vCPU"},
                {"value": 8, "label": "8 vCPU"},
            ],
            "ramOptions": [
                {"value": 1, "label": "1 GB"},
                {"value": 2, "label": "2 GB"},
                {"value": 3, "label": "3 GB"},
                {"value": 4, "label": "4 GB"},
                {"value": 5, "label": "5 GB"},
                {"value": 7, "label": "6 GB"},
                {"value": 7, "label": "7 GB"},
                {"value": 8, "label": "8 GB"},
            ],
            "diskOptions": [
                {"value": 10, "label": "10 GB"},
                {"value": 20, "label": "20 GB"},
                {"value": 30, "label": "30 GB"},
                {"value": 40, "label": "40 GB"},
                {"value": 50, "label": "50 GB"},
                {"value": 60, "label": "60 GB"},
                {"value": 70, "label": "70 GB"},
                {"value": 80, "label": "80 GB"},
            ],
            "environmentTypes": [
                {"value": "gui", "label": "GUI"},
                {"value": "cli", "label": "CLI"},
            ],
            "keyboardLayouts": [
                {"value": "cs", "label": "Čeština"},
                {"value": "en-us", "label": "English (US)"},
            ],
        }

# dnes
options_repository: OptionsRepository = StaticOptionsRepository()

# až bude DB (odkomentuješ tohle, zakomentuješ řádek nad):
# options_repo: OptionsRepository = DbOptionsRepository(connection=nejake_pripojeni)