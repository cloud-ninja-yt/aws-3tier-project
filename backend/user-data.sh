#!/bin/bash
# This script is run on the EC2 instance at launch time
sudo yum update -y
sudo yum install python3 python3-pip git -y
sudo pip3 install Flask PyMySQL requests flask-cors

# python3 app.py &