#!/bin/bash

# Asset Tracker EC2 Deployment Script
echo "🚀 Deploying Asset Tracker to EC2..."

# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
sudo apt-get install -y python3 python3-pip python3-venv

# Install nginx
sudo apt-get install -y nginx

# Install git
sudo apt-get install -y git

# Create application directory
sudo mkdir -p /var/www/asset-tracker
sudo chown ubuntu:ubuntu /var/www/asset-tracker

# Clone repository
cd /var/www/asset-tracker
git clone https://github.com/Pycube-FP/DA_Workflows.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Create gunicorn service file
sudo tee /etc/systemd/system/asset-tracker.service > /dev/null <<EOF
[Unit]
Description=Asset Tracker Gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/asset-tracker
Environment="PATH=/var/www/asset-tracker/venv/bin"
ExecStart=/var/www/asset-tracker/venv/bin/gunicorn --workers 3 --bind unix:/var/www/asset-tracker/asset-tracker.sock app:app

[Install]
WantedBy=multi-user.target
EOF

# Configure nginx
sudo tee /etc/nginx/sites-available/asset-tracker > /dev/null <<EOF
server {
    listen 80;
    server_name ec2-3-145-0-78.us-east-2.compute.amazonaws.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/asset-tracker/asset-tracker.sock;
    }

    location /static {
        alias /var/www/asset-tracker/static;
    }
}
EOF

# Enable nginx site
sudo ln -s /etc/nginx/sites-available/asset-tracker /etc/nginx/sites-enabled
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Start services
sudo systemctl start asset-tracker
sudo systemctl enable asset-tracker
sudo systemctl restart nginx

echo "✅ Deployment complete!"
echo "🌐 Your app is now available at: http://ec2-3-145-0-78.us-east-2.compute.amazonaws.com" 