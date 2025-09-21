import sys
import time
import questionary
import os
import yaml
#setup file for new users

"""
Checklist:
asking variables:
  - minecraft server ip
  - minecraft shutdown time
  - github token
  - dyna pass and ip
  - HA server (ip and button id's)
"""
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

def github_setup(account_made):
    clear_console()
    print("This code will be using two other GitHub projects, and to download and update them we will use the GitHub API")
    print("It uses your token to download files from the repo's")
    if not account_made:
        print("I see you do not have an account yet, you need to make one for this program")
        questionary.press_any_key_to_continue("Continue once you have made your account").ask()
    print("Now go to github.com")
    questionary.press_any_key_to_continue("Continue once you have opened GitHub").ask()
    print("Now click on your profile (top-right) > Settings > Developer settings > Personal Access Tokens > Tokens (classic) > Generate new token > Generate new token (classic)")
    print("Now just give it a name like Minecraft manager, set an experation and copy the key")
    github_token = questionary.password("Paste your GitHub token here:").ask()
    return github_token

def shutdown_mode_setup():
    clear_console()
    print("This code is made to shutdown your server after a set amount of time where no one is online")
    if questionary.confirm("Would you like to enable that?").ask():
        shutdown_mode = True
        shutdown_time = questionary.text(
            "After how many minutes of inactivity should the server shutdown?",
            validate=lambda val: val.isdigit() or "Enter a number"
            ).ask()
    else:
        shutdown_mode, shutdown_time = False, None
    
    return shutdown_mode, shutdown_time

def main():
    print("Hi, there!")
    print("This is a program for fully managing your minecraft server")

    linux_check()

    clear_console()

    program_location = os.path.realpath(__file__).removesuffix("\\msm\\config\\configuration.py")
    if questionary.confirm(f"Are you sure you want to use this: {program_location} location for this program?").ask():
        print("Great, let's continue")
    else:
        print("Please move this program to the location you want to use and run it again.")
        time.sleep(3)
        sys.exit(0)
    
    questionary.press_any_key_to_continue("I am going to ask you a few questions to set everything up.").ask()


    home_assistant = questionary.confirm("Do you want to use Home Assistant?").ask()

    dynu = questionary.confirm("Do you want to set-up dynu for dynamic dns?").ask()

    github_account = questionary.confirm("Do you already have a GitHub account?").ask()

    variables_to_save = {}

    if home_assistant:
        home_assistant_ip, home_assistant_token = home_assistant_setup()
        active, ip, token =  True, home_assistant_ip, home_assistant_token
    else:
        active, ip, token = False, None, None
    
    variables_to_save["HOME_ASSISTANT"] = {"active": active, "ip": ip, "token": token}

    if dynu:
        dynu_password, dynu_domain = dynu_setup()
        active, password, domain = True, dynu_password, dynu_domain
    else:
        active, password, domain = False, None, None
    
    variables_to_save["DYNU"] = {"active": active, "password": password, "domain": domain}

    github_token = github_setup(github_account)
    variables_to_save["GITHUB"] = {"token": github_token}   

    clear_console()

    print("Now that we have all of the services set-up, let's set up your minecraft server")

    shutdown_mode, shutdown_time = shutdown_mode_setup()
    variables_to_save["Shutdown"] = {"auto_shutdown": shutdown_mode, "shutdown_time": shutdown_time}
    #install the minecraft server, install the minecraft bot

    print("Now that we have all those values let's save them to a .yaml file")
    print("You should never share this file as it will give access to all of the services you added just now")

    with open('msm/config/config.yaml', 'w') as f:
        yaml.dump(variables_to_save, f, default_flow_style=False, indent=2)

if __name__ == "__main__":
    main()