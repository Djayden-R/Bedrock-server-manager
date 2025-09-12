import os
import psutil
from datetime import datetime
from msm.config.load_config import Config
import requests

HA_URL = Config().yaml("ha_url")
HA_TOKEN = Config().secret("ha_token")

LOCAL_BACKUP = Config().yaml("local_backup")
HDD_BACKUP = Config().yaml("hdd_backup")

def get_backup_folders(location):
    """Gets every folder in the location and sorts them"""
    backup_folders = sorted(
        folder for folder in os.listdir(location) 
        if os.path.isdir(os.path.join(location,folder))) 
    return backup_folders

def get_sorted_list(base_path, backup_folders):
    """
    Function wil return a dictionary with dates 
    and their the backups in a list eg. "24-03-2025":["backup1", "backup2"]
    """
    backup_per_date = {}
    for folder in backup_folders:
        folder_path = os.path.join(base_path, folder)
        backups = os.listdir(folder_path)
        backup_per_date.update({folder:backups})
    return backup_per_date

def remove_oldest_backup(backup_dates, backup_per_date, base_path, freed_space):
    for date in backup_dates:
        if len(backup_per_date[date]) > 1:
            oldest_backup_date = date
            oldest_backups = sorted(backup_per_date[oldest_backup_date])
            oldest_backup = oldest_backups[0]

            oldest_backup_path = os.path.join(base_path, oldest_backup_date, oldest_backup)
            oldest_backup_size = os.path.getsize(oldest_backup_path) / (1024 ** 3)  # Convert to GB
            
            print(f"\nRemoving old backup from {oldest_backup_date} folder: {oldest_backups}")
            print(f"Oldest backup: {oldest_backup} ({oldest_backup_size:.2f} GB)")
            print(f"Removing old backup: {oldest_backup_date} at {oldest_backup}")
            os.remove(oldest_backup_path)  # Uncomment to actually remove the file
            freed_space += oldest_backup_size
            # Remove the backup from the dictionary to avoid trying to delete it again
            backup_per_date[oldest_backup_date].remove(oldest_backup)
            return freed_space  # Only remove one file per function call

    return freed_space

def clear_old_backups(backup_per_date, required_free_space, base_path):
    """Function will remove old backups based on the folder name (the date) and name of the backup (the time). 
    The backup_per_date is a dictionary in this format: "24-03-2025":["backup1", "backup2"]"""

    all_dates = backup_per_date.keys()

    last_7_days = []
    last_30_days = []
    old_backups = []

    amount_backups_last_7 = 0
    amount_backups_last_30 = 0
    amount_backups_old = 0

    freed_space = 0

    for date in all_dates:
        date_object = datetime.strptime(date, "%Y-%m-%d")
        current_date = datetime.now()
        days_ago = (current_date - date_object).days #calculate how old the backup is in days
        if days_ago <= 7:
            last_7_days.append(date)
        elif days_ago <= 30:
            last_30_days.append(date)
        else:
            old_backups.append(date)

    print(f"Last 7 days backups: {last_7_days} with a total of {amount_backups_last_7} backups")
    print(f"Last 30 days backups: {last_30_days} with a total of {amount_backups_last_30} backups")
    print(f"Old backups: {old_backups} with a total of {amount_backups_old} backups")
    
    previous_freed_space = -1

    while freed_space < required_free_space:
        #check to prevent infinite loops
        if freed_space == previous_freed_space:
            print(f"No more space can be freed. Current freed space: {freed_space:.2f} GB, Required: {required_free_space:.2f} GB")
            break
        previous_freed_space = freed_space
        
        if old_backups:
            directory = old_backups
        elif last_30_days:
            directory = last_30_days
        elif freed_space < required_free_space:
            print("ERROR - No more old backups to remove, but not enough space freed.")
            break

        freed_space = remove_oldest_backup(directory, backup_per_date, base_path, freed_space)
    print(f"Total freed space: {freed_space:.2f} GB")

def clear_duplicate_files(backup_folders, base_path, backup_per_date):
    """Function will check for duplicate files in the backup folders
    based on size and remove them"""

    size_list = []
    duplicates = 0

    for folder in backup_folders:
        folder_path = os.path.join(base_path, folder)
        backups = os.listdir(folder_path)

        for backup in backups:
            backup_path = os.path.join(folder_path, backup)
            size = os.path.getsize(backup_path)
            
            #file is new
            if size not in size_list:
                size_list.append(size)

            #file might be a duplicate, so we remove it
            #we don't use a checksum, because it is slow and many backups aren't exact duplicates
            else:
                print("Duplicate found")
                duplicates += 1
                os.remove(backup_path) #for testing purposes we don't want to delete files
                print(f"Removed {backup_path} with size {size/(1024**3):.2f} GB")

                # Remove the backup from the dictionary to keep it in sync
                if folder in backup_per_date and backup in backup_per_date[folder]:
                    backup_per_date[folder].remove(backup)

    return duplicates

def clear_backups(location, required_free_space):

    backup_folders = get_backup_folders(location)
    backup_per_date = get_sorted_list(location, backup_folders)

    duplicates_amount = clear_duplicate_files(backup_folders, location, backup_per_date)
    clear_old_backups(backup_per_date, required_free_space, location)
    
    print(f"There are a total of {duplicates_amount} duplicate files found, all of them were removed")

def check_and_clear(location, min_free_gb, name):
    space_left = psutil.disk_usage(location).free / (1024 ** 3)

    print(f"{name} free space: {space_left:.2f} GB")

    if space_left < min_free_gb:
        print(f"Less than {min_free_gb} GB left on {name}, clearing backup's...")
        required_free_space = min_free_gb - space_left #in GB
        clear_backups(location, required_free_space)
    else:
        print(f"More than {min_free_gb} GB left on {name}, no need to clear backups.")

def main():
    check_and_clear(LOCAL_BACKUP, 30, "Local Backup")
    check_and_clear(HDD_BACKUP, 50, "HDD Backup")

if __name__ == '__main__':
    main()
