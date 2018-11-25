#!/bin/sh
echo "running apt-get -y update"
sudo apt-get -y update
echo "installing pip3"
sudo apt-get install -y python3-pip
echo "installing flask"
sudo pip3 install flask
echo "Exporting variables"
export APP_URL="0.0.0.0"
#echo "Starting Server"
#python3 restapi.py --isso da ruim por algum motivo
