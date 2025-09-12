import dotenv
import yaml

class Import_variables:
    def __init__(self):
        self.yaml_values = self.load_yaml()
        self.env_values = self.load_env()

    def load_yaml(yaml_path):
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def load_env():
        env_path = dotenv.find_dotenv(usecwd=True)
        values = dict(dotenv.dotenv_values(env_path))
        return values
    
    def secret(self, key):
        try:
            return self.env_values[key]
        except ValueError:
            print(f"Key is invalid: {key} does not exist in .env")
    
    def yaml(self, key):
        try:
            return self.yaml_values[key]
        except ValueError:
            print(f"Key is invalid: {key} does not exist in config.yaml")

