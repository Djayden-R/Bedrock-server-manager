#!/bin/bash
sudo apt-get update
sudo apt-get upgrade -y

sudo apt-get install python3-venv -y

python3 -m venv venv
source venv/bin/activate

pip install -e .
minecraft-server-manager