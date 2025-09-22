from requests import get
import urllib3
from msm.config.load_config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def entity_status(cfg: Config):
    url = f"{cfg.ha_url}/api/states/{cfg.auto_shutdown_entity}"
    
    headers = {
        "Authorization": f"Bearer {cfg.ha_token}",
        "content-type": "application/json",
    }

    response = get(url, headers=headers, verify=False)
    if response.status_code in [200, 201]:
        dictionary = response.json()
        status = dictionary["state"]
        return status == "on"
    else:
        return True
