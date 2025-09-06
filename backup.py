import os
import datetime
import subprocess
from time import monotonic

'''CONFIG'''
#directories you want to backup
raw_directories = ["~/boot_scripts", "~/minecraft_bedrock"]
#make directories work with ~
directories = [os.path.expanduser(path) for path in raw_directories]
#path for local backup's
local_backup = os.path.expanduser( "~/backup")
#path for  HDD backup's
hdd_backup = "/mnt/backup"
#Google Drive name (in rclone), must have a : after its name
Google_Drive_name = "mcbackup:"
'''END OF CONFIG'''

def generate_file_name():
    #generate a name including the date for identification
    date = datetime.datetime.now()

    folder_name = date.strftime("%Y-%m-%d")

    name = f"{date.strftime('backup_%H-%M-%S')}.zip"
    print(f"Name of the file is: '{name}'")

    backup_path = f"{local_backup}/{folder_name}/{name}"
    return backup_path, folder_name

def generate_zip(backup_path):
    command = subprocess.run(["zip","-r",backup_path,*directories], capture_output=True)
    print("Zip file generated")

def backup_HDD(backup_path, foldername):
    #check if hdd folder exists and then make a copy of the zip file to the hdd
    if not os.path.exists(hdd_backup):
        raise ValueError("HDD backup directory not found")
    else:
        subprocess.run(["cp", backup_path, f"{hdd_backup}/{foldername}"])
        print("Backup copied to hardrive")

def backup_Google_Drive(backup_symlink, folder, filename):
    t_beginning = monotonic()
    #start by creating the neccesarry folders
    subprocess.run(["rclone", "mkdir", f"{Google_Drive_name}{folder}"])

    #create a copy of the backup to Google Drive
    print("Starting upload to Google Drive...")
    
    #resolve the symlink to an actual path
    backup_path = os.path.realpath(backup_symlink)

    subprocess.run(["rclone", "copyto", backup_path, f"{Google_Drive_name}{folder}/{filename}"])

    print(f"Google Drive upload successful, took {monotonic()-t_beginning:.1f} seconds")


def update_sym_link(backup_path):
    symlink = f"{local_backup}/latest_backup.zip"

    #check if symlink already exists
    if os.path.islink(symlink):
        os.unlink(symlink)
    
    #save latest backup to a symlink, so it can be accessed later for the Google Drive backup
    os.symlink(backup_path, symlink)
    print(f"Symlink: '{symlink}' points to '{backup_path}'")

def quick_backup():
    #check if directories exist and if local backup doesn't, it creates it
    if not directories:
        raise ValueError("Please add the directories you want to backup to 'directories'")
    if not os.path.exists(local_backup):
        os.makedirs(local_backup)
        print(f"Created folder: '{local_backup}'")
    
    #generate name and a folder with today's date, if it doesn't exist already from an earlier backup
    backup_path, folder_name = generate_file_name()

    local_folder = f"{local_backup}/{folder_name}"
    hdd_folder = f"{hdd_backup}/{folder_name}"

    for folder in [local_folder, hdd_folder]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Created backup folder for today: '{folder}'")
    
    generate_zip(backup_path) #generate zip in local folder
    backup_HDD(backup_path, folder_name) #copy the zip to hdd location

    update_sym_link(backup_path) #update symlink for later backup's

def drive_backup():
    date = datetime.datetime.now() - datetime.timedelta(days=1) #the update is from the day before, so this is calculated
    folder = date.strftime("backup/%y-%m-%d")
    filename = date.strftime("backup_%H-%M-%S.zip")
    latest_backup_path = f"{local_backup}/latest_backup.zip" #refer to symlink to the latest backup

    backup_Google_Drive(latest_backup_path, folder, filename)

def main(type="quick"): #check correct action, "quick" or "drive"
    if type == "quick":
        quick_backup()
    elif type == "drive":
        drive_backup()

if __name__ == "__main__":
    while True:
        type_backup = input("Give type of backup, quick (1) or drive (2): ")
        if type_backup not in ["1", "2"]:
            print("not valid, try again")
        else:
            if type_backup == "1":
                main(type="quick")
                break
            elif type_backup == "2":
                main(type="drive")
                break

