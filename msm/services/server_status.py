from mcstatus import BedrockServer
from time import sleep
from datetime import datetime
from msm.config.load_config import Config

def start_checking_playercount(cfg: Config) -> bool:
    if cfg.mc_ip and cfg.timing_shutdown:
        server = BedrockServer(str(cfg.mc_ip), cfg.mc_port)
        amount_of_checks = int(cfg.timing_shutdown / 10)
    else:
        raise ValueError(f"Cannot check player count: {'Minecraft ip not defined' if not cfg.mc_ip else ''} {'and timing not defined' if not cfg.timing_shutdown else ''}")
    
    times_no_one = 0
    server_used = False

    while True:
        try:
            status = server.status() #type: ignore
            online_players = status.players.online
        except Exception as e:
            print(f"[{datetime.now()}] Error checking server status: {e}")
            status = None  # ensure it's defined
            sleep(5)
            continue

        if online_players == 0:
            times_no_one += 1
            print(f"[{datetime.now()}] No one online ({times_no_one}/{amount_of_checks})")
        elif online_players > 0:
            print(f"[{datetime.now()}] Someone online")
            times_no_one = 0
            server_used = True
        else:
            print(f"[{datetime.now()}] Unexpected value: {status.players.online}")

        if times_no_one == amount_of_checks:
            if server_used:
                return True #backup needed
            else:
                return False #no backup needed

        sleep(10)

