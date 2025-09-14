from github import Github, Auth
import requests
import os
import subprocess
from msm.config.load_config import Config

repo_name = "MCXboxBroadcast/Broadcaster"

cfg = Config()
GITHUB_TOKEN = cfg.secret("github_token")
BEDROCK_BOT_PATH = cfg.yaml("bedrock_bot_path")

def download(url, name):
        r = requests.get(url, stream=True)

        with open(name, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def get_latest_release(repo_name, filename):
    # using an access token
    auth = Auth.Token(GITHUB_TOKEN)

    # Public Web Github
    g = Github(auth=auth)

    repo = g.get_repo(repo_name)
    latest_version = repo.get_latest_release()

    for asset in latest_version.get_assets():
        if asset.name == filename:
            download(asset.browser_download_url, filename)
            if os.path.exists(f"{os.path.dirname(os.path.abspath(__file__))}/{filename}"):
                print("File is successfully downloaded")
            else:
                print("Problem during download")
            break

    # To close connections after use
    g.close()

def update_bedrock_bot():
    get_latest_release(repo_name, "MCXboxBroadcastStandalone.jar")
    subprocess.run(["rm", f"{BEDROCK_BOT_PATH}/MCXboxBroadcastStandalone.jar"])
    subprocess.run(["mv", "MCXboxBroadcastStandalone.jar", BEDROCK_BOT_PATH])

def update_minecraft_server():
    minecraft_updater_path = os.path.expanduser("~/minecraft_server/updater/mcserver_autoupdater.py")
    subprocess.run(['python3', minecraft_updater_path])

def main():
    update_bedrock_bot()
    update_minecraft_server()

if __name__ == "__main__":
    main()
