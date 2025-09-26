import requests
from datetime import datetime
from msm.config.load_config import Config

url = "https://api.dynu.com/nic/update"

def update_DNS(cfg: Config):

    params = {
        "hostname": cfg.dynu_domain,
        "password": cfg.dynu_pass,
    }

    response = requests.get(url, params=params)

    if "good" in response.text:
        print(f"[{datetime.now()}] DDNS update successful")
    else:
        print(f"[{datetime.now()}] DDNS update failed:", response.text)

if __name__ == "__main__":
    update_DNS()