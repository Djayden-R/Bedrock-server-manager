from requests import get
import urllib3
from load_config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HA_URL = Config().yaml("ha_url")
HA_TOKEN = Config().secret("ha_token")

def entity_status(entity_id="input_boolean.auto_shutdown"):
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
