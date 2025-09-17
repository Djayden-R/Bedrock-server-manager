from requests import get
import urllib3
from msm.config.load_config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

cfg = Config()
HA_URL = cfg.yaml("ha_url")
HA_TOKEN = cfg.secret("ha_token")
AUTO_SHUTDOWN_ENTITY = "input_boolean.auto_shutdown"

def entity_status(entity_id=AUTO_SHUTDOWN_ENTITY):
    url = f"{HA_URL}/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {HA_TOKEN}",
        "content-type": "application/json",
    }

    response = get(url, headers=headers, verify=False)
    if response.status_code in [200, 201]:
        dictionary = response.json()
        status = dictionary["state"]
        return status == "on"
    else:
        return True
