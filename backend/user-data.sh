#!/bin/bash
# This script is run on the EC2 instance at launch time

# Update all packages
sudo yum update -y

# Install Python3, pip, and git
sudo yum install python3 python3-pip git -y

# Install necessary Python packages
sudo pip3 install Flask PyMySQL requests flask-cors boto3

# Set the environment variables for the database connection
export SECRET_NAME='NAME-OF-YOUR-SECRET-GOES-HERE'
export DB_HOST='DATABASE-ENDPOINT-GOES-HERE'

# Clone the project repository from GitHub
git clone https://github.com/cloud-ninja-yt/aws-3tier-project.git

# Change directory to the backend folder of the cloned repository
cd aws-3tier-project/backend

# Start the Flask application in the background
python3 app.py &