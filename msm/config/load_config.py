import yaml
import os

class Config:
    def __init__(self):
        self.yaml_values = self.load_yaml(f"{os.path.realpath(__file__).removesuffix("load_config.py")}config.yaml")

    def load_yaml(self, yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    
    def load(self, key):
        try:
            return self.yaml_values[key]
        except ValueError:
            print(f"Key is invalid: {key} does not exist in config.yaml")

