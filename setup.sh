#!/bin/bash
set -e

#update and upgrade system packages
sudo apt-get update
sudo apt-get upgrade -y

#install required system packages for Minecraft updater
sudo apt-get install -y python3 python3-pip python3-venv wget unzip tmux libcurl4

#create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

#install and run the program
pip install -e .
bedrock-server-manager