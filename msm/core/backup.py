import os
import datetime
import subprocess
from time import monotonic
from msm.config.load_config import Config
import shutil
import tempfile
from typing import Optional
from pathlib import Path

def generate_file_name(cfg: Config):
    #generate a name including the date for identification
    date = datetime.datetime.now()

    folder_name = date.strftime("%Y-%m-%d")
    backup_name = date.strftime('backup_%H-%M-%S')
    
    print(f"Name of the file will be: '{backup_name}.zip'")

    return backup_name, folder_name

def generate_zip(cfg: Config, backup_name: str) -> Optional[Path]:
    #move directories to a temp directory and make a zip file from that temp directory
    if cfg.backup_directories:
        with tempfile.TemporaryDirectory() as temp_dir:
            for directory in cfg.backup_directories:
                directory = Path(directory)
                #get name and new location of directory that is getting backed up
                temp_dest = os.path.join(temp_dir, directory.name)
                #copy directory to destination
                shutil.copytree(directory, temp_dest)
            shutil.make_archive(backup_name, "zip", temp_dir)
        print("Zip file generated")
        return Path(os.path.abspath(os.path.dirname(__file__)))
    else:
        print("There are no backup directories defined")
        return None

def backup_drive(cfg: Config, backup_symlink: Path, folder: str, filename: str):
    t_beginning = monotonic()
    #create the backup folder
    subprocess.run(["rclone", "mkdir", f"{cfg.backup_drive_name}{folder}"])

    print("Starting upload to drive...")
    
    #get the actual path from the symlink
    backup_path = os.path.realpath(backup_symlink)

    #upload to drive via rclone
    subprocess.run(["rclone", "copyto", backup_path, f"{cfg.backup_drive_name}{folder}/{filename}"])

    print(f"Drive upload successful, took {monotonic()-t_beginning:.1f} seconds")


def update_sym_link(cfg: Config, backup_path: Path):
    if cfg.backup_local_path:
        location = cfg.backup_local_path
    elif cfg.backup_hdd_path:
        location = cfg.backup_hdd_path
    else:
        return
    
    symlink = os.path.join(location, "latest_backup.zip")

    #check if symlink already exists
    if os.path.islink(symlink):
        os.unlink(symlink)
    
    #save latest backup to a symlink, so it can be accessed later for the drive backup
    os.symlink(backup_path, symlink)
    print(f"Symlink: '{symlink}' points to '{backup_path}'")

def quick_backup(cfg: Config):
    #check if directories exist and if local backup doesn't, it creates it
    if not cfg.backup_directories:
        raise ValueError("Please add the directories you want to backup to 'directories'")
    
    if not (cfg.backup_local_path or cfg.backup_hdd_path):
        return

    #generate name and a folder with today's date, if it doesn't exist already from an earlier backup
    backup_name, folder_name = generate_file_name(cfg)

    #check if backup locations and folders exist and create them if the don't
    for backup_location in [cfg.backup_local_path, cfg.backup_local_path]:
        if backup_location:
            backup_folder = os.path.join(backup_location, folder_name)
            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)
                print(f"Created backup folder for today: '{backup_folder}'")
    
    temp_backup_folder = generate_zip(cfg, backup_name) #generate a temporary zip file in main folder
    
    if not temp_backup_folder:
        return

    temp_backup_path = Path(os.path.join(temp_backup_folder, f"{backup_name}.zip"))
    
    #copy the temp backup to the local folder and/or the hdd folder
    if cfg.backup_local_path:
        backup_folder = os.path.join(cfg.backup_local_path, folder_name)
        shutil.copy(temp_backup_path, backup_folder)
        update_sym_link(cfg, temp_backup_path) #update symlink for later backup's

    if cfg.backup_hdd_path:
        backup_folder = os.path.join(cfg.backup_hdd_path, folder_name)
        shutil.copy(temp_backup_path, backup_folder)

def drive_backup(cfg: Config):
    date = datetime.datetime.now() - datetime.timedelta(days=1) #the update is from the day before, so this is calculated
    folder = date.strftime("backup/%y-%m-%d")
    filename = date.strftime("backup_%H-%M-%S.zip")
    if cfg.backup_local_path:
        latest_backup_path = Path(os.path.join(cfg.backup_local_path, "latest_backup.zip")) #refer to symlink to the latest backup
        backup_drive(cfg, latest_backup_path, folder, filename)
    else:
        raise ValueError("Local backup is not defined")

def main(cfg: Config, type: str = "quick"): #check correct action, "quick" or "drive"
    if type == "quick":
        quick_backup(cfg)
    elif type == "drive":
        drive_backup(cfg)

