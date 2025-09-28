from git import Repo
import requests
import os
import subprocess
from msm.config.load_config import Config
from shutil import rmtree
from pathlib import Path

bedrockbot_repo = "MCXboxBroadcast/Broadcaster"
minecraft_updater_repo = "ghwns9652/Minecraft-Bedrock-Server-Updater"

def download(url, file_path):
        r = requests.get(url, stream=True)

        with open(file_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

def get_latest_release(repo_name, download_location, filename=None):
    url = f"https://api.github.com/repos/{repo_name}/releases/latest"

    response = requests.get(url)
    response.raise_for_status()
    release = response.json()

    for asset in release["assets"]:

        if asset["name"] == filename:

            #location fo where file will be saved
            file_path = f"{download_location}/{asset['name']}"

            #remove file if it already exists
            if os.path.exists(file_path):
                os.remove(file_path)
            
            #download file to it's location
            download(asset["browser_download_url"], file_path)

            #check if file downloaded successfully
            if os.path.exists(file_path):
                print("File is successfully downloaded")
            else:
                print("Problem during download")

def get_bedrock_bot(cfg: Config):
    if cfg.path_base:
        bedrock_bot_path = os.path.join(cfg.path_base, "bedrock_connector")
        if os.path.exists(bedrock_bot_path):
            rmtree(bedrock_bot_path)
        os.makedirs(bedrock_bot_path, exist_ok=True)

        get_latest_release(bedrockbot_repo, bedrock_bot_path, filename="MCXboxBroadcastStandalone.jar")
    else:
        print("Cannot get connector bot, since base path is not defined")

def get_minecraft_updater(cfg: Config):
    if cfg.path_base:
        mc_updater_path = os.path.join(cfg.path_base, "minecraft_updater")
        if os.path.exists(mc_updater_path):
            rmtree(mc_updater_path)
        Repo.clone_from(f"https://github.com/{minecraft_updater_repo}.git", mc_updater_path)
    else:
        print("Cannot get Minecraft updater, since download location is not defined")

def update_minecraft_server(cfg: Config):
    if cfg.path_base:
        mc_updater_path = os.path.join(cfg.path_base, "minecraft_updater")
        minecraft_updater_path = os.path.expanduser(f"{mc_updater_path}/updater/mcserver_autoupdater.py")
        subprocess.run(['python3', minecraft_updater_path])
    else:
        print("Cannot update Minecraft server, since base path is not defined")

def main(cfg: Config):
    get_bedrock_bot(cfg)
    update_minecraft_server(cfg)