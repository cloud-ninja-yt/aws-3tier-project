#!/bin/bash
# This script is run on the EC2 instance at launch time
# It installs the necessary packages and starts the web server

# Update all packages
sudo yum update -y

# Install Node.js, npm, git, and nginx
sudo yum install -y nodejs npm git nginx

# Clone the project repository from GitHub
git clone https://github.com/cloud-ninja-yt/aws-3tier-project.git

# Create a new React app named 'corn-app-frontend'
npx create-react-app corn-app-frontend

# Change directory to the newly created React app
cd corn-app-frontend

# Move the App component and image from the cloned repository to the src directory
mv -f /aws-3tier-project/frontend/App.* src/
mv /aws-3tier-project/frontend/corn.png src/

# Move the nginx configuration file to the appropriate directory
mv /aws-3tier-project/config/nginx.conf /etc/nginx/conf.d/cornhub.conf

# Install axios for making HTTP requests
sudo npm install axios

# Install 'serve' globally to serve the built React app
sudo npm install -g serve

# Build the React app
npm run build

# Start nginx
sudo systemctl start nginx

# Enable nginx to start on boot
sudo systemctl enable nginx