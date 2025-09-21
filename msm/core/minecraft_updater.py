from github import Github, Auth
import requests
import os
import subprocess
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from msm.config.load_config import Config

bedrockbot_repo = "MCXboxBroadcast/Broadcaster"

cfg = Config()
GITHUB_TOKEN = cfg.load("github_token")
BEDROCK_BOT_PATH = cfg.load("bedrock_bot_path")

def download(url, file_path):
        r = requests.get(url, stream=True)

        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def get_latest_release(repo_name, download_location, filename=None):
    # using an access token
    auth = Auth.Token(GITHUB_TOKEN)

    # Public Web Github
    g = Github(auth=auth)

    repo = g.get_repo(repo_name)
    latest_version = repo.get_latest_release()

    for asset in latest_version.get_assets():

        if asset.name == filename or filename == None:

            #location fo where file will be saved
            file_path = f"{download_location}/{asset.name}"

            #remove file if it already exists
            if os.path.exists(file_path):
                subprocess.run(["rm", file_path])
            
            #download file to it's location
            download(asset.browser_download_url, file_path)

            #check if file downloaded successfully
            if os.path.exists(file_path):
                print("File is successfully downloaded")
            else:
                print("Problem during download")

    # To close connections after use
    g.close()

def get_bedrock_bot():
    get_latest_release(bedrockbot_repo, BEDROCK_BOT_PATH , filename="MCXboxBroadcastStandalone.jar")

def update_minecraft_server():
    minecraft_updater_path = os.path.expanduser("~/minecraft_server/updater/mcserver_autoupdater.py")
    subprocess.run(['python3', minecraft_updater_path])

def main():
    get_bedrock_bot()
    update_minecraft_server()

if __name__ == "__main__":
    main()
