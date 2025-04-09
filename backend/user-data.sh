#!/bin/bash
# This script is run on the EC2 instance at launch time
sudo yum update -y
sudo yum install python3 python3-pip git -y
sudo pip3 install Flask PyMySQL requests flask-cors
git clone https://github.com/cloud-ninja-yt/aws-3tier-project.git
cd aws-3tier-project/backend
# python3 app.py &