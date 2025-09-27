import os
import datetime
import subprocess
from time import monotonic
from msm.config.load_config import Config
import shutil
import tempfile

def generate_file_name(cfg: Config):
    #generate a name including the date for identification
    date = datetime.datetime.now()

    folder_name = date.strftime("%Y-%m-%d")

    backup_name = date.strftime('backup_%H-%M-%S')

    backup_path = f"{cfg.backup_local_path}/{folder_name}/{backup_name}.zip"
    
    print(f"Name of the file will be: '{backup_name}.zip'")

    return backup_path, backup_name, folder_name

def generate_zip(cfg: Config, backup_name):
    #move directories to a temp directory
    if cfg.backup_directories:
        with tempfile.TemporaryDirectory() as temp_dir:
            for directory in cfg.backup_directories:
                dir_name = os.path.basename(directory.rstrip('/\\'))
                temp_dest = os.path.join(temp_dir, dir_name)
                shutil.copytree(directory, temp_dest)
            shutil.make_archive(backup_name, "zip", temp_dir)
        print("Zip file generated")
    else:
        print("There are no backup directories defined")

def backup_HDD(cfg: Config, backup_path, foldername):
    #check if hdd folder exists and then make a copy of the zip file to the hdd
    if not cfg.backup_hdd_path or not os.path.exists(cfg.backup_hdd_path):
        raise ValueError("HDD backup directory not found")
    else:
        subprocess.run(["cp", backup_path, f"{cfg.backup_hdd_path}/{foldername}"])
        print("Backup copied to hardrive")

def backup_drive(cfg: Config, backup_symlink, folder, filename):
    t_beginning = monotonic()
    #create the backup folder
    subprocess.run(["rclone", "mkdir", f"{cfg.backup_drive_name}{folder}"])

    print("Starting upload to drive...")
    
    #get the actual path from the symlink
    backup_path = os.path.realpath(backup_symlink)

    #upload to drive via rclone
    subprocess.run(["rclone", "copyto", backup_path, f"{cfg.backup_drive_name}{folder}/{filename}"])

    print(f"Drive upload successful, took {monotonic()-t_beginning:.1f} seconds")


def update_sym_link(cfg: Config, backup_path):
    symlink = f"{cfg.backup_local_path}/latest_backup.zip"

    #check if symlink already exists
    if os.path.islink(symlink):
        os.unlink(symlink)
    
    #save latest backup to a symlink, so it can be accessed later for the Google Drive backup
    os.symlink(backup_path, symlink)
    print(f"Symlink: '{symlink}' points to '{backup_path}'")

def quick_backup(cfg: Config):
    #check if directories exist and if local backup doesn't, it creates it
    if not cfg.backup_directories:
        raise ValueError("Please add the directories you want to backup to 'directories'")
    if cfg.backup_local_path:
        if not os.path.exists(cfg.backup_local_path):
            os.makedirs(cfg.backup_local_path)
            print(f"Created folder: '{cfg.backup_local_path}'")
    else:
        print("Local backup location is not defined")

    #generate name and a folder with today's date, if it doesn't exist already from an earlier backup
    backup_path, backup_name, folder_name = generate_file_name(cfg)

    local_folder = f"{cfg.backup_local_path}/{folder_name}"
    hdd_folder = f"{cfg.backup_local_path}/{folder_name}"

    for folder in [local_folder, hdd_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created backup folder for today: '{folder}'")
    
    generate_zip(cfg, backup_name) #generate zip in local folder

    backup_HDD(cfg, backup_path, folder_name) #copy the zip to hdd location

    update_sym_link(cfg, backup_path) #update symlink for later backup's

def drive_backup(cfg: Config):
    date = datetime.datetime.now() - datetime.timedelta(days=1) #the update is from the day before, so this is calculated
    folder = date.strftime("backup/%y-%m-%d")
    filename = date.strftime("backup_%H-%M-%S.zip")
    latest_backup_path = f"{cfg.backup_local_path}/latest_backup.zip" #refer to symlink to the latest backup

    backup_drive(cfg, latest_backup_path, folder, filename)

def main(cfg: Config, type="quick"): #check correct action, "quick" or "drive"
    if type == "quick":
        quick_backup(cfg)
    elif type == "drive":
        drive_backup(cfg)

