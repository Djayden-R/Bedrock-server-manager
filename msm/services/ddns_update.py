import requests
from datetime import datetime
from dotenv import load_dotenv
from msm.config.load_config import Config

cfg = Config()
ddns_domain = cfg.yaml("ddns_domain")
ddns_password = cfg.secret("ddns_password")

url = "https://api.dynu.com/nic/update"

params = {
    "hostname": ddns_domain,
    "password": ddns_password,
}

def update_DNS():
    response = requests.get(url, params=params)

    if "good" in response.text:
        print(f"[{datetime.now()}] DDNS update successful")
    else:
        print(f"[{datetime.now()}] DDNS update failed:", response.text)

if __name__ == "__main__":
    update_DNS()