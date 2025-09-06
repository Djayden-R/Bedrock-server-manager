import requests
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://api.dynu.com/nic/update"

params = {
    "hostname": "broke.theworkpc.com",
    "password": os.getenv("DDNS_PASSWORD")
}

def update_DNS():
    response = requests.get(url, params=params)

    if "good" in response.text:
        print(f"[{datetime.now()}] DDNS update successful")
    else:
        print(f"[{datetime.now()}] DDNS update failed:", response.text)

if __name__ == "__main__":
    update_DNS()