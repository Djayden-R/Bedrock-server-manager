# Bedrock Server Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Ubuntu-orange)](https://ubuntu.com/)
[![GitHub last commit](https://img.shields.io/github/last-commit/Djayden-R/Bedrock-server-manager)](https://github.com/Djayden-R/Bedrock-server-manager)

An automated management tool for a bedrock server. It will handle updating, shutting down, making backups, handling a dynamic dns, and even connecting players on a console to the server.

## How it Works

After setup, the program determines which mode to run based on configuration and timing:

- **NORMAL** - Standard operating mode that updates the DNS and then updates the server if needed and lastly starts the server with automatic shutdown after inactivity
- **DRIVE_BACKUP** - Initiates backup to online drive using the latest symlink via Rclone  
- **INVALID** - Triggered when server starts outside configured valid hours
- **CONFIGURATION** - First-time setup mode when no config.yaml exists

## Prerequisites

> **Note:** This program has been tested exclusively on Ubuntu. Ubuntu is the recommended platform. For drive backup functionality, Rclone must be configured separately (tutorial below).

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
or after adding the alias
```bash
bsm
```

## Features

- **Home Assistant Integration** - Remote control via IP, token, and entity switches for auto shutdown and updates
- **Backup Management** - Multiple backup strategies including local, external drive, and cloud storage using Rclone  
- **Intelligent Scheduling** - Configurable operating hours and automatic shutdown timeouts
- **Dynamic DNS** - DynuDNS integration for consistent server addressing

## Extra tutorials

To automatically start this program on boot, follow [**this tutorial**](https://www.youtube.com/watch?v=Un9ASbGCN0U).

To configure Rclone follow one of these tutorials:
- [**for Google Drive**](https://www.youtube.com/watch?v=FQuMFrazK1Y)
- [**for Onedrive**](https://www.youtube.com/watch?v=dTFt2DkOde4)

## Acknowledgments

This project integrates the following open-source tools:

- **[Broadcaster](https://github.com/MCXboxBroadcast/Broadcaster)** (GPL-3.0 License) - Console bridge functionality
- **[Minecraft-Bedrock-Server-Updater](https://github.com/ghwns9652/Minecraft-Bedrock-Server-Updater)** (MIT License) - Server update automation

## Development Notes

AI assistance was utilized for specific components: `pyproject.toml` configuration, `load_config.py` implementation, and formatting of the `README.md`.
