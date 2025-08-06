# 🚀 EC2 Deployment Guide

## 📋 **Prerequisites**
- EC2 instance running (ec2-3-145-0-78.us-east-2.compute.amazonaws.com)
- SSH access to EC2 instance
- PEM key file for authentication

## 🔑 **Step 1: Connect to EC2**

### **Using SSH (Windows):**
```bash
ssh -i "DA_Workflows.pem" ubuntu@ec2-3-145-0-78.us-east-2.compute.amazonaws.com
```

### **Using PuTTY (Windows):**
1. Convert PEM to PPK using PuTTYgen
2. Connect using PuTTY with the PPK file

## 🚀 **Step 2: Deploy Application**

### **Option A: Run Deployment Script**
```bash
# Upload deploy.sh to EC2
scp -i "DA_Workflows.pem" deploy.sh ubuntu@ec2-3-145-0-78.us-east-2.compute.amazonaws.com:~/

# SSH into EC2 and run deployment
ssh -i "DA_Workflows.pem" ubuntu@ec2-3-145-0-78.us-east-2.compute.amazonaws.com
chmod +x deploy.sh
./deploy.sh
```

### **Option B: Manual Deployment**
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install dependencies
sudo apt-get install -y python3 python3-pip python3-venv nginx git

# Clone repository
cd /var/www
sudo mkdir asset-tracker
sudo chown ubuntu:ubuntu asset-tracker
cd asset-tracker
git clone https://github.com/Pycube-FP/DA_Workflows.git .

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn

# Configure Gunicorn service
sudo nano /etc/systemd/system/asset-tracker.service
# (Add the service configuration from deploy.sh)

# Configure Nginx
sudo nano /etc/nginx/sites-available/asset-tracker
# (Add the nginx configuration from deploy.sh)

# Enable and start services
sudo systemctl enable asset-tracker
sudo systemctl start asset-tracker
sudo ln -s /etc/nginx/sites-available/asset-tracker /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## 🔧 **Step 3: Configure Security Groups**

### **AWS Console:**
1. Go to EC2 Dashboard
2. Select your instance
3. Click "Security" tab
4. Click "Security Groups"
5. Add inbound rules:
   - **HTTP (80)**: 0.0.0.0/0
   - **HTTPS (443)**: 0.0.0.0/0 (if using SSL)
   - **SSH (22)**: Your IP address

## 🌐 **Step 4: Access Your App**

### **Web Access:**
- **URL**: http://ec2-3-145-0-78.us-east-2.compute.amazonaws.com
- **Mobile**: Same URL - install as PWA

### **Check Status:**
```bash
# Check service status
sudo systemctl status asset-tracker
sudo systemctl status nginx

# Check logs
sudo journalctl -u asset-tracker -f
sudo tail -f /var/log/nginx/error.log
```

## 📱 **Step 5: Mobile Installation**

### **After deployment:**
1. **Open browser** on mobile device
2. **Go to**: http://ec2-3-145-0-78.us-east-2.compute.amazonaws.com
3. **Install app**:
   - **Android**: Tap "Install" in Chrome
   - **iPhone**: Tap Share → "Add to Home Screen"
4. **Use like native app**!

## 🔄 **Step 6: Updates**

### **To update the app:**
```bash
# SSH into EC2
ssh -i "DA_Workflows.pem" ubuntu@ec2-3-145-0-78.us-east-2.compute.amazonaws.com

# Pull latest code
cd /var/www/asset-tracker
git pull origin main

# Restart service
sudo systemctl restart asset-tracker
```

## 🎯 **Demo Script**

*"This Asset Tracker is now deployed on AWS EC2 and accessible worldwide. Users can visit the URL from any device and install it as a Progressive Web App on their phone or tablet. It provides the full experience of a native mobile app without needing app store approval."*

## ✅ **Deployment Checklist**

- [ ] Code pushed to GitHub ✅
- [ ] EC2 instance running
- [ ] Security groups configured
- [ ] Application deployed
- [ ] Nginx configured
- [ ] Services running
- [ ] Mobile access tested
- [ ] PWA installation tested
- [ ] Demo ready! 🎉

**Your app will be live at: http://ec2-3-145-0-78.us-east-2.compute.amazonaws.com** 🌍✨ 