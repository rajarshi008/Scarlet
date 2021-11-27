#!/bin/bash

sudo apt-get install python3-virtualenv
sudo apt-get install redis-server

virtualenv -p python3 venv

source venv/bin/activate
pip install -r requirements.txt
