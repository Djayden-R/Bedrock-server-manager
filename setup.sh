#!/bin/bash
set -e

#update and upgrade system packages
sudo apt-get update
sudo apt-get upgrade -y

#install required system packages for Minecraft updater, and also install java for the console bridge
sudo apt-get install -y python3 python3-pip python3-venv wget unzip tmux libcurl4 default-jdk

#create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

#install and run the program
pip install -e .
bedrock-server-manager