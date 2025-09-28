# Minecraft Bedrock Server Manager
An automated management tool for a bedrock server. It will handle updating, shutting down, making backups, handling a dynamic dns, and even connecting players on a console to the server.

## How this works
After it has been set up the program will check what mode it needs to run:
- **NORMAL** - the mode that runs when the server should just start up
- **DRIVE_BACKUP** - the mode that will start the backup to your online drive. It will take the latest symlink and upload it using Rclone
- **INVALID** - this mode is triggered when the server is started at an invalid time (set by the user)
- **UPDATE** - this mode is turned on when the Home Assistant switch for updating is turned on during boot
- **CONFIGURATION** - run when the program is opened for the first time (based on if the config.yaml exists)

## Prerequisites
This program has only been tested on Ubuntu. It is therefore recommended you use Ubuntu for this program, and if you want to use drive backups, you will need to setup Rclone (tutorial is not provided).

## How to run
### 1. First time setup
```bash
git clone https://github.com/Djayden-R/Minecraft-bedrock-server-manager.git
cd Minecraft-bedrock-server-manager
chmod +x setup.sh
./setup.sh
```
This will run the setup process and will ask you all the questions needed for setting up the program

### 2. Normal operation
```bash
./venv/bin/minecraft-server-manager
```
Since the program is installed inside a virtual environment you will need to run the program like this

## Configuration
- **Home Assistant Integration** - IP, token, and entity switches for turning on auto shutdown and updates
- **Backup Settings** - Local, external drive, and cloud backup locations (using Rclone)
- **Server Timing** - Valid operating hours and shutdown timeouts
- **Dynamic DNS** - DynuDNS integration for one fixed server address

## Extra Step
I recommend setting up a .service file that automatically starts the program, this way the server only has to be turned on to just work. For turning on the server I use a Discord bot that runs on Home Assistant and sends a WoL signal to the server.
