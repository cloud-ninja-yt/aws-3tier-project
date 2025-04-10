#!/bin/bash
# This script is run on the EC2 instance at launch time
sudo yum update -y
sudo yum install python3 python3-pip git -y
sudo pip3 install Flask PyMySQL requests flask-cors boto3

# Set the environment variables
export SECRET_NAME="rds!cluster-b033ef22-e3e0-48e2-b906-fb80d49134b5"
export DB_HOST="database-1.cluster-cv6cme66eplp.us-east-1.rds.amazonaws.com"

git clone https://github.com/cloud-ninja-yt/aws-3tier-project.git
cd aws-3tier-project/backend
# python3 app.py &