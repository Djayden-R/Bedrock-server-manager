# Bedrock Server Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Ubuntu-orange)](https://ubuntu.com/)
[![GitHub last commit](https://img.shields.io/github/last-commit/Djayden-R/Bedrock-server-manager)](https://github.com/Djayden-R/Bedrock-server-manager)

An automated management tool for a bedrock server. It will handle updating, shutting down, making backups, handling a dynamic dns, and even connecting players on a console to the server.

## How it Works

After setup, the program determines which mode to run based on configuration and timing:

- **NORMAL** - Standard operating mode that starts the server with automatic shutdown after inactivity
- **DRIVE_BACKUP** - Initiates backup to online drive using the latest symlink via Rclone  
- **INVALID** - Triggered when server starts outside configured valid hours
- **UPDATE** - Activated when Home Assistant update switch is enabled during boot
- **CONFIGURATION** - First-time setup mode when no config.yaml exists

## Prerequisites

> **Note:** This program has been tested exclusively on Ubuntu. Ubuntu is the recommended platform. For drive backup functionality, Rclone must be configured separately.

## Installation

### Initial Setup

```bash
git clone https://github.com/Djayden-R/Bedrock-server-manager.git
cd Bedrock-server-manager
chmod +x setup.sh
./setup.sh
```

The setup script will guide you through the configuration process.

### Running the Server

```bash
./Bedrock-server-manager/venv/bin/bedrock-server-manager
```

**Optional:** Create a shell alias for easier access:

```bash
# Add to ~/.bashrc
echo 'alias bsm="$HOME/Bedrock-server-manager/venv/bin/bedrock-server-manager"' >> ~/.bashrc
source ~/.bashrc
```
Now you can just run the program using bsm
```bash
bsm
```

## Features

- **Home Assistant Integration** - Remote control via IP, token, and entity switches for auto shutdown and updates
- **Backup Management** - Multiple backup strategies including local, external drive, and cloud storage using Rclone  
- **Intelligent Scheduling** - Configurable operating hours and automatic shutdown timeouts
- **Dynamic DNS** - DynuDNS integration for consistent server addressing

## Production Deployment

For automated server management, consider setting up a systemd service file. This enables the server to start automatically on boot.

**Additional Setup:** The author uses a Discord bot running on Home Assistant to send Wake-on-LAN signals for remote server startup.

## Acknowledgments

This project integrates the following open-source tools:

- **[Broadcaster](https://github.com/MCXboxBroadcast/Broadcaster)** (GPL-3.0 License) - Console bridge functionality
- **[Minecraft-Bedrock-Server-Updater](https://github.com/ghwns9652/Minecraft-Bedrock-Server-Updater)** (MIT License) - Server update automation

## Development Notes

AI assistance was utilized for specific components: `pyproject.toml` configuration, `load_config.py` implementation, and formatting of the `README.md`.
