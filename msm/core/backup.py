import os
import datetime
import subprocess
from time import monotonic
from msm.config.load_config import Config

def generate_file_name(cfg: Config):
    #generate a name including the date for identification
    date = datetime.datetime.now()

    folder_name = date.strftime("%Y-%m-%d")

    name = f"{date.strftime('backup_%H-%M-%S')}.zip"
    print(f"Name of the file is: '{name}'")

    backup_path = f"{cfg.local_backup_path}/{folder_name}/{name}"
    return backup_path, folder_name

def generate_zip(backup_path, cfg: Config):
    command = subprocess.run(["zip","-r",backup_path,*cfg.directories], capture_output=True)
    print("Zip file generated")

def backup_HDD(backup_path, foldername, cfg: Config):
    #check if hdd folder exists and then make a copy of the zip file to the hdd
    if not os.path.exists(cfg.hdd_backup_path):
        raise ValueError("HDD backup directory not found")
    else:
        subprocess.run(["cp", backup_path, f"{cfg.hdd_backup_path}/{foldername}"])
        print("Backup copied to hardrive")

def backup_Google_Drive(cfg: Config, backup_symlink, folder, filename):
    t_beginning = monotonic()
    #start by creating the neccesarry folders
    subprocess.run(["rclone", "mkdir", f"{cfg.google_drive_name}{folder}"])

    #create a copy of the backup to Google Drive
    print("Starting upload to Google Drive...")
    
    #resolve the symlink to an actual path
    backup_path = os.path.realpath(backup_symlink)

    subprocess.run(["rclone", "copyto", backup_path, f"{cfg.google_drive_name}{folder}/{filename}"])

    print(f"Google Drive upload successful, took {monotonic()-t_beginning:.1f} seconds")


def update_sym_link(cfg: Config,backup_path):
    symlink = f"{cfg.local_backup_path}/latest_backup.zip"

    #check if symlink already exists
    if os.path.islink(symlink):
        os.unlink(symlink)
    
    #save latest backup to a symlink, so it can be accessed later for the Google Drive backup
    os.symlink(backup_path, symlink)
    print(f"Symlink: '{symlink}' points to '{backup_path}'")

def quick_backup(cfg: Config):
    #check if directories exist and if local backup doesn't, it creates it
    if not cfg.directories:
        raise ValueError("Please add the directories you want to backup to 'directories'")
    if not os.path.exists(cfg.local_backup_path):
        os.makedirs(cfg.local_backup_path)
        print(f"Created folder: '{cfg.local_backup_path}'")

    #generate name and a folder with today's date, if it doesn't exist already from an earlier backup
    backup_path, folder_name = generate_file_name()

    local_folder = f"{cfg.local_backup_path}/{folder_name}"
    hdd_folder = f"{cfg.hdd_backup_path}/{folder_name}"

    for folder in [local_folder, hdd_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created backup folder for today: '{folder}'")
    
    generate_zip(backup_path) #generate zip in local folder
    backup_HDD(backup_path, folder_name) #copy the zip to hdd location

    update_sym_link(backup_path) #update symlink for later backup's

def drive_backup(cfg: Config):
    date = datetime.datetime.now() - datetime.timedelta(days=1) #the update is from the day before, so this is calculated
    folder = date.strftime("backup/%y-%m-%d")
    filename = date.strftime("backup_%H-%M-%S.zip")
    latest_backup_path = f"{cfg.local_backup_path}/latest_backup.zip" #refer to symlink to the latest backup

    backup_Google_Drive(latest_backup_path, folder, filename)

def main(cfg: Config, type="quick"): #check correct action, "quick" or "drive"
    if type == "quick":
        quick_backup(cfg)
    elif type == "drive":
        drive_backup(cfg)

