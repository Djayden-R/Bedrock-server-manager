import yaml
from pathlib import Path
from dataclasses import dataclass

@dataclass
class Config:
    update_switch: str
    begin_valid_time: int
    end_valid_time: int
    backup_time: int

    @classmethod
    def load(cls, path: Path = Path("config.yaml")) -> "Config":
        data = yaml.safe_load(path.read_text())
        return cls(**data)

