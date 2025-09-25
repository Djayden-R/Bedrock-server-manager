import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List

@dataclass(frozen=True)
class HomeAssistant:
    ip: str
    token: str

@dataclass(frozen=True)
class Dynu:
    password: str
    domain: str

@dataclass(frozen=True)
class Backups:
    backup_directories: List[str]
    drive_backup_path: Optional[str] = None
    hdd_backup_path: Optional[str] = None
    local_backup_path: Optional[str] = None

@dataclass(frozen=True)
class Shutdown:
    shutdown_time: str

@dataclass(frozen=True)
class Config:
    home_assistant: Optional[HomeAssistant] = None
    dynu: Optional[Dynu] = None
    backups: Optional[Backups] = None
    shutdown: Optional[Shutdown] = None

    @classmethod
    def load(cls, path: Path = Path("config.yaml")) -> "Config":
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
            
        data = yaml.safe_load(path.read_text())
        
        # Convert nested dicts to dataclass instances
        home_assistant = HomeAssistant(**data["home_assistant"]) if "home_assistant" in data else None
        dynu = Dynu(**data["dynu_dns"]) if "dynu_dns" in data else None  # Note: your YAML uses "dynu_dns"
        backups = Backups(**data["backups"]) if "backups" in data else None
        shutdown = Shutdown(**data["shutdown"]) if "shutdown" in data else None
        
        return cls(
            home_assistant=home_assistant,
            dynu=dynu,
            backups=backups,
            shutdown=shutdown
        )