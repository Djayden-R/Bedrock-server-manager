from mcstatus import BedrockServer
from time import sleep
from datetime import datetime

server = BedrockServer(MC_server_ip, MC_server_port)
amount_of_checks = int(shutdown_time/delay)

def start_checking_playercount():
    times_no_one = 0
    server_used = False

    while True:
        try:
            status = server.status()
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

        sleep(delay)

