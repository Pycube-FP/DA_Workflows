#!/usr/bin/env python3
"""
Asset Usage & Rental Tracking System - Installation Script
This script will install all dependencies and set up the system
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}:")
        print(f"   Command: {command}")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main installation function"""
    print("🏥 Asset Usage & Rental Tracking System - Installation")
    print("=" * 60)
    
    # Check Python version
    print(f"🐍 Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        sys.exit(1)
    
    # Upgrade pip first
    print("\n📦 Upgrading pip...")
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        print("⚠️  Warning: Could not upgrade pip, continuing anyway...")
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements"):
        print("❌ Failed to install dependencies. Please try manually:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    directories = ["templates", "static"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Test imports
    print("\n🧪 Testing imports...")
    try:
        import flask
        import flask_sqlalchemy
        import flask_login
        import qrcode
        import bcrypt
        print("✅ All required modules imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)
    
    print("\n🎉 Installation completed successfully!")
    print("\n🚀 To start the system:")
    print("   python app.py")
    print("\n📍 Access the system at: http://localhost:5000")
    print("👤 Login with: admin / admin123")
    
    # Ask if user wants to start the system
    response = input("\n🤔 Would you like to start the system now? (y/n): ")
    if response.lower() in ['y', 'yes']:
        print("\n🚀 Starting the system...")
        os.system(f"{sys.executable} app.py")

if __name__ == "__main__":
    main() 