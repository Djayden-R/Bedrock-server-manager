from msm.services.ddns_update import update_DNS
from msm.services.server_status import check_playercount
from msm.services.check_ha_switch import entity_status
from msm.config.load_config import Config
import msm.core.backup as backup
from msm.core.minecraft_updater import get_console_bridge, update_minecraft_server
import sys
from datetime import datetime
from enum import Enum
import subprocess
import os
from time import sleep

class Mode(Enum):
    NORMAL = "normal" #normal operating mode, shutdown after 3 minutes with local backup and hdd backup
    DRIVE_BACKUP = "drive backup" #just backup to drive, then shutdown
    INVALID = "invalid time" #boot up at an invalid time, just shutdown
    CONFIGURATION = "config" #go through set-up process

def shutdown():
    print("Shutting down in 10 seconds")
    print("ctrl + c to cancel")
    subprocess.run(["sudo", "shutdown", "now"])

def hour_valid(hour: int) -> bool:
    if cfg.timing_begin_valid and cfg.timing_end_valid:
        return cfg.timing_begin_valid < hour < cfg.timing_end_valid
    else: 
        return False

def get_mode():
    #check if new user
    try:
        global cfg 
        cfg = Config.load()
    except FileNotFoundError:
        return Mode.CONFIGURATION
    
    time = datetime.now()
    hour = time.hour
    print(f"[{datetime.now()}] Current hour: {hour}")
    if not (cfg.timing_begin_valid and cfg.timing_end_valid) or hour_valid(hour):
            return Mode.NORMAL
    elif hour == cfg.timing_drive_backup:
        return Mode.DRIVE_BACKUP
    else:
        return Mode.INVALID

def start_server(cfg: Config):
    if cfg.path_base:
        mc_updater_path = os.path.join(cfg.path_base, "minecraft_updater")
        subprocess.run(['bash', mc_updater_path+'/updater/startserver.sh', mc_updater_path])
    else:
        raise ValueError("Base path is not defined")

def stop_server(cfg: Config):
    if cfg.path_base:
        mc_updater_path = os.path.join(cfg.path_base, "minecraft_updater")
        subprocess.run(['bash', mc_updater_path+'/updater/stopserver.sh', mc_updater_path])
        sleep(10)
    else:
        raise ValueError("Base path is not defined")

def normal_operation():
    if cfg.dynu_domain and cfg.dynu_pass:
        update_DNS(cfg)
    
    if update_minecraft_server(cfg): #if server needed an update, also update the console bridge
        get_console_bridge(cfg)
        shutdown()
    else: #if server wasn't updated, start the server manually
        start_server(cfg)
    
    if cfg.timing_shutdown:
        needs_backup = check_playercount(cfg)
        if needs_backup == True: #server needs backup
            if entity_status(cfg, cfg.ha_shutdown_entity): #type: ignore
                print(f"[{datetime.now()}] Shutting down Minecraft server...")
                stop_server(cfg)
                if cfg.backup_directories:
                    print(f"[{datetime.now()}] Starting backup script")
                    backup.main(cfg, type="quick")
                else:
                    print(f"[{datetime.now()}] No backup directories, skipping backup")
                print(f"[{datetime.now()}] Shutting down...")
                shutdown()
        elif needs_backup == False: #server doesn't need backup
            if entity_status(cfg, cfg.ha_shutdown_entity): #type: ignore
                print(f"[{datetime.now()}] No one online, but server was not used, so backup is not needed")
                print(f"[{datetime.now()}] Shutting down Minecraft server...")
                stop_server(cfg)
                print(f"[{datetime.now()}] Shutting down...")
                shutdown()
        elif needs_backup is None: #error occured
            return
    else:
        print("WARNING - Auto shutdown is off, this is not reccomended, backups will not work")
        


def drive_backup():
    print(f"[{datetime.now()}] Only backing up to drive")
    backup.main(cfg, type="drive")
    print(f"[{datetime.now()}] Shutting down...")
    shutdown()

def update_server():
    get_console_bridge(cfg)
    update_minecraft_server(cfg)

def main():
    mode = get_mode()
    print(f"[{datetime.now()}] Current mode: {mode.value}")

    if mode == Mode.NORMAL:
        normal_operation()
    elif mode == Mode.DRIVE_BACKUP:
        drive_backup()
    elif mode == Mode.INVALID:
        print(f"[{datetime.now()}] Invalid time, shutting down")
        shutdown()
        sys.exit(1)
    elif mode == Mode.CONFIGURATION:
        from msm.config import configuration
        configuration.main()


