from socket import socket
import sys
import time
import questionary
import os
import yaml
import socket
from msm.config.load_config import Config
import msm.core.minecraft_updater
import subprocess
import ipaddress
from pathlib import Path

#setup file for new users
def linux_check():
    if sys.platform != "linux":
        print("You are not running Linux. This program will not work as expected.")
        input("Press enter to continue or ctrl+c to exit.")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def password_confirm() -> str:
    dynu_password = questionary.password("What is your ddns password?").ask()
    dynu_password_confirm = questionary.password("Please confirm your ddns password.").ask()
    if dynu_password != dynu_password_confirm:
        print("Passwords do not match. Please try again.")
        return password_confirm()
    return dynu_password

def dynu_setup():
    print("Let's configure dynu.")
    print("First you must go to https://www.dynu.com and create an account")
    questionary.press_any_key_to_continue("Press enter once you have created an account.").ask()

    print("Nice, now let's get you a custom DNS address")
    if not questionary.confirm("You should be on the control panel, correct?").ask():
        print("No problem! Just go to https://www.dynu.com/en-US/ControlPanel or click on the settings icon.")

    print("There you must click on \"DDNS Services\" and then \"Add\"")
    print("Follow the prompts to create a new DDNS service.")
    questionary.press_any_key_to_continue("Press enter once you have created a DDNS service.").ask()

    print("Great! Now just add a password to your DDNS service.")
    print("Click on the link next to the red flag \"IP Update Password\"")
    print("And then enter a strong password into the \"New IP Update Password\" and confirm field.")
    questionary.press_any_key_to_continue("Press enter once you have added a password.").ask()

    print("Now that we got your DDNS service set up, let's get your password and domain.")

    dynu_password = password_confirm()
    dynu_domain = questionary.text("What is your dynu domain?").ask()
    return dynu_password, dynu_domain

def home_assistant_setup():
    clear_console()
    print("Home Assistant will be used for some automatic tasks, like updating and backups")
    print("But in order to use Home Assistant we will need its ip and token")
    home_assistant_ip = questionary.text("What is you Home Assistant address?", validate=lambda val: val.startswith("http://") or val.startswith("https://") or "Must start with http:// or https://", default="http://").ask() #type: ignore
    print("Getting your token is fairly easy")
    print("Go to your profile in the bottom-left corner, then to the security tab.\nAt the bottom you will see long lived access token, create one, name it something like Bedrock server manager")
    print("Then paste the token bellow")
    home_assistant_token = questionary.password("Home Assistant token:").ask()
    clear_console()
    print("Now we have to set up a switch")
    print("First make a switch for turning on and off auto shutdown (useful for debugging)")
    print("Go to settings > devices and services > helpers > add (switch)")
    auto_shutdown_entity = questionary.text("Name of switch: ", validate=lambda val: val.startswith("input_boolean.") or "helper must be a switch", default="input_boolean.").ask() #type: ignore
    return home_assistant_ip, home_assistant_token, auto_shutdown_entity

def shutdown_mode_setup(drive_enabled: bool):
    clear_console()
    print("This code is made to shutdown your server after a set amount of time where no one is online")
    if questionary.confirm("Would you like to enable that?").ask():
        shutdown_time = int(questionary.text(
            "After how many minutes of inactivity should the server shutdown?",
            validate=lambda val: val.isdigit() or "Enter a number" #type: ignore
        ).ask())
        if questionary.confirm("It is also possible to enable certain timeframes where the server will not startup.\nWould you like to enable that?").ask():
            begin_valid_time = int(questionary.text(
                "Enter the start time in 24h format HH",
                validate=lambda val: val.isdigit() and 0 <= int(val.removeprefix("0") if len(val) > 1 else val) < 24 or "Enter a valid time in HH format" #type: ignore
            ).ask().removeprefix("0"))
            end_valid_time = int(questionary.text(
                "Enter the end time in 24h format (HH)",
                validate=lambda val: val.isdigit() and 0 <= int(val.removeprefix("0") if len(val) > 1 else val) < 24 or "Enter a valid time in HH format" #type: ignore
            ).ask().removeprefix("0"))
        begin_valid_time = end_valid_time = None
    else:
        shutdown_time = begin_valid_time = end_valid_time = None
    
    if drive_enabled:
        drive_backup_time = int(questionary.text(
            "At what time do you want the server to create drive backup?",
                validate=lambda val: val.isdigit() and 0 <= int(val.removeprefix("0")) < 24 or "Enter a valid time in HH format", #type: ignore
                default="3"
                ).ask().removeprefix("0"))
    else:
        drive_backup_time = None
    return shutdown_time, begin_valid_time, end_valid_time, drive_backup_time

def automatic_backups_setup(default_path: Path) -> tuple[Path, Path | None, str | None, list[Path]]:
    clear_console()
    backup_options = questionary.checkbox(
        "There are different options for automatic backups, select the ones you want to use:",
        choices=["Local backup", "Back up to external drive", "Drive backup"],
        validate=lambda var: True if "Local backup" in var else "Local backup is required"
    ).ask()
    
    hdd_backup = "Back up to external drive" in backup_options
    drive_backup = "Drive backup" in backup_options

    local_path = Path(questionary.path(
        "Where do you want to save the local backups?\n DO NOT select the main folder for this project, since backups will also contain previous backups",
        default=os.path.join(str(default_path).removesuffix("Bedrock-server-manager"), "backups"),
        only_directories=True
    ).ask())
    
    if hdd_backup:
        hdd_path = Path(questionary.path(
            "Where do you want to save the external drive backups?",
            default="/mnt",
            only_directories=True
        ).ask()) 
    else:
        hdd_path = None
    if drive_backup:
        print("You will need rclone for drive backups, so make sure you have it set up")
        drive_name = str(questionary.text(
            "What is the name of your rclone remote? (something like 'drive:')",
            validate=lambda val: val.endswith(":") or "Remote name must end with ':'" #type: ignore
        ).ask())
    else:
        drive_name = None

    directories: list[Path] = []
    while True:
        directory = Path(questionary.path(
            "Enter a directory to back up (or leave blank to finish):",
            only_directories=True,
            default=str(default_path)
        ).ask())
        if not directory:
            break
        directories.append(directory)
    return local_path, hdd_path, drive_name, directories

def get_minecraft_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

def add_alias():
    subprocess.run(['bash', '-c', 'echo \'alias bsm="$HOME/Bedrock-server-manager/venv/bin/bedrock-server-manager"\' >> ~/.bashrc'])

def main():
    print("Hi, there!")
    print("This is a program for fully managing your bedrock server")

    linux_check()

    clear_console()

    #gather all variables and save them to a dictionary
    config_data = {}

    program_location = Path(os.path.realpath(__file__).removesuffix("\\msm\\config\\configuration.py").removesuffix("/msm/config/configuration.py"))
    if questionary.confirm(f"{program_location} \nAre you sure you want to use the above location for this program?").ask():
        print("Great, let's continue")
        config_data["path"] = {"base": program_location}
    else:
        print("Please move this program to the location you want to use and run it again.")
        time.sleep(3)
        sys.exit(0)
    
    questionary.press_any_key_to_continue("I am going to ask you a few questions to set everything up.").ask()


    """ 
    DISABLED SERVICE SELECTION
    Don't have time to make services optional yet
    This will be implemented in the future
    """

    # services = questionary.checkbox(
    # "What services do you want to set up?", choices=["Home Assistant", "Dynu DNS", "Automatic shutdown", "Automatic backups"]).ask()


    # home_assistant = "Home Assistant" in services
    # dynu = "Dynu DNS" in services
    # auto_shutdown = "Automatic shutdown" in services
    # auto_backup = "Automatic backups" in services


    home_assistant = dynu = auto_backup = auto_shutdown = True

    if home_assistant:
        ha_ip, ha_token, auto_shutdown_entity = home_assistant_setup()
        config_data["ha"] = {"ip": ha_ip, "token": ha_token, "shutdown_entity": auto_shutdown_entity}

    if dynu:
        dynu_password, dynu_domain = dynu_setup()
        config_data["dynu"] = {"pass": dynu_password, "domain": dynu_domain}

    if auto_backup:
        local_path, hdd_path, drive_name, directories = automatic_backups_setup(program_location)
        config_data["backup"] = {k: v for k, v in [("local_path", local_path), ("hdd_path", hdd_path), ("drive_name", drive_name), ("directories", directories)] if v is not None} #type: ignore
    else:
        drive_name = None
    
    if auto_backup and drive_name:
        drive_enabled = True
    else:
        drive_enabled = False
    
    if auto_shutdown:
        shutdown_time, begin_valid_time, end_valid_time, drive_backup_time = shutdown_mode_setup(drive_enabled)
        config_data["timing"] = {k: v for k, v in [("shutdown", shutdown_time), ("begin_valid", begin_valid_time), ("end_valid", end_valid_time), ("drive_backup", drive_backup_time)] if v is not None} #type: ignore


    clear_console()
    
    #automatically get the users ip and confirm if it's right
    mc_ip = get_minecraft_ip()

    def validate_local_ip(ip: str) -> bool:
        try:
            adress = ipaddress.ip_address(ip)
            return adress.is_private or adress.is_loopback or adress.is_link_local
        except Exception:
            return False

    if not questionary.confirm(f"Is this your local ip: {mc_ip}").ask():
        mc_ip = questionary.text("Please add your local ip:",
                 default= "192.168.1.1",
                 validate=validate_local_ip
        ).ask()

    #ask for the minecraft port (type checking is not needed, because variable is always string)
    mc_port = int(questionary.text("Enter the Minecraft server port:", default="19132", validate=lambda x: x.isdigit()).ask()) # type: ignore
    
    #save the minecraft data
    config_data["mc"] = {"ip": mc_ip, "port": mc_port}
    clear_console()

    #save the file and warn the user if it contains sensitive information
    with open('msm/config/config.yaml', 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False, indent=2)
        print("Config file saved to msm/config/config.yaml")

    if dynu or home_assistant:
        print("Never share this file with anyone as it will give access to all of the services you configured")
    
    #load config we just saved
    cfg = Config.load()

    #ask permission to download the repositories
    print("This program can uses MCXboxBroadcast/Broadcaster to make it possible for console players to join the server, this is optional")
    
    #install and configure the console bridge
    if questionary.confirm("Do you want to download this program?").ask():
        print("Great, downloading now")
        msm.core.minecraft_updater.get_console_bridge(cfg)
        msm.core.minecraft_updater.authenticate_console_bridge(cfg)
        questionary.press_any_key_to_continue("Press any key if you understand the instructions")
    
    #install the minecraft updater and run it to also install the minecraft server
    msm.core.minecraft_updater.get_minecraft_updater(cfg)
    msm.core.minecraft_updater.update_minecraft_server(cfg)

    #ask if the user wants an alias and add it if they do
    print("An alias makes it possible to run this program by just typing 'bsm' into the terminal")
    if not questionary.confirm("Have you added an alias for this program before").ask():
        if questionary.confirm("Would you like to add an alias").ask():
            add_alias()
    
    #give instructions for running the program
    print("To make this code work, first reboot this computer and then run 'bsm'")
    print("If you want the code to run on boot, follow the tutorial inside the README.md")

if __name__ == "__main__":
    main()