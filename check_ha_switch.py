from requests import get
import urllib3
import dotenv
import os

dotenv.load_dotenv()


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def entity_status(entity_id="input_boolean.auto_shutdown"):
    token = os.getenv("HASS_TOKEN")
    url = f"http://192.168.1.185:8123/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "content-type": "application/json",
    }

    response = get(url, headers=headers, verify=False)
    if response.status_code in [200, 201]:
        dictionary = response.json()
        status = dictionary["state"]
        return status == "on"
    else:
        return True
