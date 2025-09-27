from msm.services.ddns_update import update_DNS
from msm.services.server_status import start_checking_playercount
from msm.services.check_ha_switch import entity_status
from msm.config.load_config import Config
import msm.core.backup as backup
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path

class Mode(Enum):
    NORMAL = "normal" #normal operating mode, shutdown after 3 minutes with local backup and hdd backup
    DRIVE_BACKUP = "drive backup" #just backup to google drive, then shutdown
    INVALID = "invalid time" #boot up at an invalid time, just shutdown
    UPDATE = "update" #update the server
    CONFIGURATION = "config" #go through set-up process

def shutdown():
	with open("/tmp/mc_ready","w") as f:
		f.write("done")

def hour_valid(hour):
    return cfg.timing_begin_valid < hour < cfg.timing_end_valid

def get_mode():
    #check if new user
    config_file = Path("msm/config/config.yaml").absolute()
    if not config_file.exists():
        print(f"[{datetime.now()}] no config found, running set-up process")
        return Mode.CONFIGURATION
    else:
        global cfg 
        cfg = Config.load()

    time = datetime.now()
    hour = time.hour
    print(f"[{datetime.now()}] current hour: {hour}")
    if hour_valid(hour):
        if entity_status(cfg, cfg.ha_update_entity):
            return Mode.UPDATE
        else:
            return Mode.NORMAL
    elif hour == cfg.timing_drive_backup:
        return Mode.DRIVE_BACKUP
    else:
        return Mode.INVALID

def normal_shutdown():
    update_DNS(cfg)
    while True:
        if start_checking_playercount(cfg):
            if entity_status(cfg, cfg.ha_shutdown_entity):
                print(f"[{datetime.now()}] starting backup script")
                backup.main(cfg, type="quick")
                print(f"[{datetime.now()}] shutting down...")
                shutdown()
                sys.exit(42)
        else:
            if entity_status(cfg, cfg.ha_shutdown_entity):
                print(f"[{datetime.now()}] no one online, but server was not used, so backup is not needed")
                shutdown()


def drive_backup():
    print(f"[{datetime.now()}] only backing up to Google Drive")
    backup.main(cfg, type="drive")
    print(f"[{datetime.now()}] shutting down...")
    shutdown()

def update_server():
    pass

def main(mode: Mode):
    if mode == Mode.NORMAL:
        normal_shutdown()
    elif mode == Mode.UPDATE:
        update_server()
    elif mode == Mode.DRIVE_BACKUP:
        drive_backup()
    elif mode == Mode.INVALID:
        print(f"[{datetime.now()}] invalid time, shutting down")
        shutdown()
        sys.exit(1)
    elif mode == Mode.CONFIGURATION:
        from msm.config import configuration
        configuration.main()

if __name__ == "__main__":
    mode = get_mode()
    print(f"[{datetime.now()}] current mode: {mode.value}")
    main(mode)


