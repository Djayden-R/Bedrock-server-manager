from git import Repo
import requests
import os
import subprocess
from msm.config.load_config import Config
from shutil import rmtree
import questionary

console_bridge_repo = "MCXboxBroadcast/Broadcaster"
minecraft_updater_repo = "ghwns9652/Minecraft-Bedrock-Server-Updater"

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

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

def get_console_bridge(cfg: Config):
    if cfg.path_base:
        console_bridge_folder = os.path.join(cfg.path_base, "console_bridge")
        console_bridge_file = os.path.join(console_bridge_folder, "MCXboxBroadcastStandalone.jar")
        if os.path.exists(console_bridge_file):
            os.remove(console_bridge_file)

        get_latest_release(console_bridge_repo, console_bridge_folder, filename="MCXboxBroadcastStandalone.jar")
    else:
        print("Cannot get console bridge, since base path is not defined")

def authenticate_console_bridge(cfg: Config):
    if cfg.path_base:
        console_bridge_path = os.path.join(cfg.path_base, "msm/console_bridge/MCXboxBroadcastStandalone.jar")
        if os.path.exists(console_bridge_path):
            process = subprocess.Popen(["java", "-jar", console_bridge_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            auth_code = None
            if process.stdout:
                for line in process.stdout:
                    if "enter the code" in line:
                        cleaned_auth_line = line.split("enter the code ")[1]
                        auth_code = cleaned_auth_line.split()[0]
                        print("Now you need to go to microsoft.com/link")
                        print(f"Then enter this code: {auth_code}")
                    elif "Successfully authenticated as" in line:
                        console_bridge_path = os.path.join(cfg.path_base, "msm/console_bridge")
                        clear_console()
                        print("Great the console bridge is now authenticated")
                        print("Only one thing, you will need to edit the config file of the bot yourself")
                        print(f"You will need to go to {console_bridge_path}")
                        print("And then you will need to 'sudo nano config.yml'")
                        print("There under session-info you will need to enter a name, ip and port")
            else:
                print("There is no output from the console bridge")
        else:
            print("Console bridge is not found")
            print(f"Checked this path: {console_bridge_path}")
    else:
        raise ValueError("Cannot authenticate console bridge, since base path is not defined")

def get_minecraft_updater(cfg: Config):
    if cfg.path_base:
        mc_updater_path = os.path.join(cfg.path_base, "minecraft_updater")
        if os.path.exists(mc_updater_path):
            if len(os.listdir(mc_updater_path)) > 1:
                print(os.listdir(mc_updater_path))
                print("WARNING - The Minecraft updater is already downloaded")
                print("Continuing could mean that your Minecraft world will be overwritten")
                if questionary.text("Confirm by writing 'DELETE':", ).ask() == "DELETE":
                    rmtree(mc_updater_path)
                else:
                    print("Didn't update minecraft_updater")
            else:
                rmtree(mc_updater_path)
                
        Repo.clone_from(f"https://github.com/{minecraft_updater_repo}.git", mc_updater_path, )
    else:
        print("Cannot get Minecraft updater, since download location is not defined")

def update_minecraft_server(cfg: Config):
    if cfg.path_base:
        mc_updater_path = os.path.join(cfg.path_base, "minecraft_updater")
        minecraft_updater_path = os.path.expanduser(f"{mc_updater_path}/updater/mcserver_autoupdater.py")
        minecraft_updater_output = subprocess.run(['python3', minecraft_updater_path], capture_output=True, text=True)
        if "minecraft server is already newest version" in minecraft_updater_output.stdout:
            print("Nothing to update, starting server")
            return False
        elif "minecraft server is updated" in minecraft_updater_output.stdout:
            print("Minecraft server successfully updated and started")
            return True
        else:
            raise ValueError(f"Unknown state: {minecraft_updater_output.stdout} \nerror: {minecraft_updater_output.stderr}")
    else:
        raise ValueError("Cannot update Minecraft server, since base path is not defined")

def main(cfg: Config):
    get_console_bridge(cfg)
    update_minecraft_server(cfg)