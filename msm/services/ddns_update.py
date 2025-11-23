import requests
from datetime import datetime
from msm.config.load_config import Config
import logging

# Get logger
log = logging.getLogger("bsm")

url = "https://api.dynu.com/nic/update"


def update_DNS(cfg: Config = None, test = False, domain = None, password = None):

    params = {
        "hostname": cfg.dynu_domain if test else domain,
        "password": cfg.dynu_pass if test else password,
    }

    response = requests.get(url, params=params)

    if "good" in response.text:
        if test:
            return True
        else:
            log.info(f"[{datetime.now()}] DDNS update successful")
    else:
        if test:
            return True
        else:
            log.error(f"[{datetime.now()}] DDNS update failed: {response.text}")
