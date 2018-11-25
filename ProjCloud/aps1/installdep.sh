#!/bin/sh
echo "running apt-get -y update"
sudo apt-get -y update
echo "installing pip3"
sudo apt-get install -y python3-pip
echo "installing flask"
sudo pip3 install flask
echo "Exporting variables"
export APP_URL="0.0.0.0"
echo "starting flask app"
python3 restapi.py