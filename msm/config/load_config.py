import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, List
import os

@dataclass(frozen=True)
class Config:
    # Home Assistant
    ha_ip: Optional[str] = None
    ha_token: Optional[str] = None
    ha_update_entity: Optional[str] = None
    ha_shutdown_entity: Optional[str] = None

    # Dynu DNS
    dynu_pass: Optional[str] = None
    dynu_domain: Optional[str] = None
    
    # Minecraft Server
    mc_ip: Optional[str] = None
    mc_port: Optional[int] = None
    
    # Backup settings
    backup_local_path: Optional[str] = None
    backup_hdd_path: Optional[str] = None
    backup_drive_name: Optional[str] = None
    backup_directories: Optional[List[str]] = None
    
    # Timing
    timing_begin_valid: Optional[str] = None
    timing_end_valid: Optional[str] = None
    timing_shutdown: Optional[int] = None
    timing_drive_backup: Optional[int] = None

    # Paths
    path_base: Optional[str] = None

    @classmethod
    def load(cls) -> "Config":
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config_location = Path(os.path.join(dir_path, "config.yaml"))

        if not config_location.exists():
            raise FileNotFoundError(f"Config file not found: {config_location}")
        
        data = yaml.safe_load(config_location.read_text())
        
        # Flatten nested structure
        flat_data = {}
        for section, values in data.items():
            if isinstance(values, dict):
                for key, value in values.items():
                    flat_data[f"{section}_{key}"] = value
            else:
                flat_data[section] = values
                
        return cls(**flat_data)