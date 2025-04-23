#!/bin/bash
# This script is run on the EC2 instance at launch time
# It installs the necessary packages and starts the web server
sudo yum update -y
sudo yum install -y nodejs npm git
git clone https://github.com/cloud-ninja-yt/aws-3tier-project.git
npx create-react-app corn-app-frontend
cd corn-app-frontend
mv -f /aws-3tier-project/frontend/App.* src/
mv /aws-3tier-project/frontend/corn.png src/
# Install axios for making HTTP requests
sudo npm install axios
sudo npm install -g serve
# Build the React app 
npm run build
# Start the React app using serve
# serve -s -n build &