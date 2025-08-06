#!/usr/bin/env python3
"""
Asset Usage & Rental Tracking System
Startup script for the hospital asset management prototype
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Error installing dependencies")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    directories = ["templates", "static"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Directories created")

def main():
    """Main startup function"""
    print("🏥 Asset Usage & Rental Tracking System")
    print("=" * 50)
    
    # Check Python version
    check_python_version()
    
    # Create directories
    create_directories()
    
    # Install requirements if needed
    if not os.path.exists("asset_tracking.db"):
        print("🔄 First time setup detected...")
        install_requirements()
    
    # Start the application
    print("\n🚀 Starting the application...")
    print("📍 Access the system at: http://localhost:5000")
    print("👤 Demo credentials: admin / admin123")
    print("\n" + "=" * 50)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 