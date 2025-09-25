import sys
import time
import questionary
import os
import yaml

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

import msm.core.minecraft_updater

#setup file for new users
def linux_check():
    if sys.platform != "linux":
        print("You are not running Linux. This program will not work as expected.")
        input("Press enter to continue or ctrl+c to exit.")

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def password_confirm():
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
    home_assistant_ip = questionary.text("What is you Home Assistant address?").ask()
    print("Getting your token is fairly easy")
    print("Go to your profile in the bottom-left corner, then to the security tab.\nAt the bottom you will see longlive accesstoken, create one, name it something like Minecraft server manager")
    print("Then paste the token bellow")
    home_assistant_token = questionary.password("Home Assistant token:").ask()
    clear_console()
    print("We will be coming back to Home Assistant later on for some more configuring, but for now we are done")
    return home_assistant_ip, home_assistant_token

def shutdown_mode_setup():
    clear_console()
    print("This code is made to shutdown your server after a set amount of time where no one is online")
    if questionary.confirm("Would you like to enable that?").ask():
        shutdown_time = questionary.text(
            "After how many minutes of inactivity should the server shutdown?",
            validate=lambda val: val.isdigit() or "Enter a number"
            ).ask()
    else:
        shutdown_time = None
    
    return shutdown_time

def automatic_backups_setup(default_path):
    clear_console()
    backup_options = questionary.checkbox(
        "There are different options for automatic backups, select the ones you want to use:",
        choices=["Local backup", "Back up to external drive", "Drive backup"]
    ).ask()
    
    local_backup = "Local backup" in backup_options
    hdd_backup = "Back up to external drive" in backup_options
    drive_backup = "Drive backup" in backup_options

    if local_backup:
        local_backup_path = questionary.path(
            "Where do you want to save the local backups?",
            default=os.path.join(default_path, "backups"),
            only_directories=True
        ).ask()
    else:
        local_backup_path = None
    
    if hdd_backup:
        hdd_backup_path = questionary.path(
            "Where do you want to save the external drive backups?",
            default="/mnt",
            only_directories=True
        ).ask() 
    else:
        hdd_backup_path = None
    if drive_backup:
        print("You will need rclone for drive backups, so make sure you have it set up")
        drive_backup_path = questionary.text(
            "What is the name of your rclone remote? (something like 'drive:')",
            validate=lambda val: val.endswith(":") or "Remote name must end with ':'"
        ).ask()
    else:
        drive_backup_path = None

    backup_directories = []
    while True:
        directory = questionary.path(
            "Enter a directory to back up (or leave blank to finish):",
            only_directories=True,
            default=default_path
        ).ask()
        if not directory:
            break
        backup_directories.append(directory)
    return local_backup_path, hdd_backup_path, drive_backup_path, backup_directories

def main():
    print("Hi, there!")
    print("This is a program for fully managing your minecraft server")

    linux_check()

    clear_console()

    program_location = os.path.realpath(__file__).removesuffix("\\msm\\config\\configuration.py")
    if questionary.confirm(f"Are you sure you want to use this location:\n {program_location} \nfor this program?").ask():
        print("Great, let's continue")
    else:
        print("Please move this program to the location you want to use and run it again.")
        time.sleep(3)
        sys.exit(0)
    
    questionary.press_any_key_to_continue("I am going to ask you a few questions to set everything up.").ask()

    services = questionary.checkbox(
    "What services do you want to set up?", choices=["Home Assistant", "Dynu DNS", "Automatic shutdown", "Automatic backups"]).ask()


    home_assistant = "Home Assistant" in services
    dynu = "Dynu DNS" in services
    auto_shutdown = "Automatic shutdown" in services
    auto_backup = "Automatic backups" in services


    #gather all variables and save them to a dictionary
    config_data = {}

    if home_assistant:
        ha_ip, ha_token = home_assistant_setup()
        config_data["home_assistant"] = {"active": True, "ip": ha_ip, "token": ha_token}

    if dynu:
        dynu_password, dynu_domain = dynu_setup()
        config_data["dynu_dns"] = {"active": True, "password": dynu_password, "domain": dynu_domain}

    if auto_shutdown:
        shutdown_time = shutdown_mode_setup()
        config_data["shutdown"] = {"shutdown_time": shutdown_time}

    if auto_backup:
        local_backup_path, hdd_backup_path, drive_backup_path, backup_directories = automatic_backups_setup(program_location)
        config_data["automatic_backups"] = {k: v for k, v in [("local_backup_path", local_backup_path), ("hdd_backup_path", hdd_backup_path), ("drive_backup_path", drive_backup_path), ("backup_directories", backup_directories)] if v is not None}

    clear_console()

    with open('msm/config/config.yaml', 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False, indent=2)
        print("Config file saved to msm/config/config.yaml")

    if dynu or home_assistant:
        print("Never share this file with anyone as it will give access to all of the services you configured")
    
    #we don't have a config yet, so we need to pass a fake config to the functions
    class FakeConfig:
        def __init__(self):
            self.bedrock_bot_path = os.path.join(project_root, "bedrock_connector")
            self.mc_updater_path = os.path.join(project_root, "minecraft_updater")
    cfg = FakeConfig()

    #ask permission to download the repositories
    print("This program can uses MCXboxBroadcast/Broadcaster to make it possible for console players to join the server")
    print("This is optional")
    if questionary.confirm("Do you want to download this program?").ask():
        print("Great, downloading now")
        msm.core.minecraft_updater.get_bedrock_bot(cfg)
    msm.core.minecraft_updater.get_minecraft_updater(cfg)

if __name__ == "__main__":
    main()