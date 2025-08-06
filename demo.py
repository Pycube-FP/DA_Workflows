#!/usr/bin/env python3
"""
Asset Usage & Rental Tracking System - Demo Script
This script demonstrates the key features of the system
"""

import requests
import time
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🏥 {title}")
    print("="*60)

def demo_asset_scanning():
    """Demonstrate asset scanning workflow"""
    print_header("Asset Scanning & Recognition Workflow")
    
    print("1️⃣ Scanning Asset INF001 (Infusion Pump)")
    print("   - QR code recognition")
    print("   - Asset validation")
    print("   - Status check: Available ✅")
    print("   - Atlas of Assets query")
    
    print("\n2️⃣ Atlas of Assets Response:")
    print("   📋 SOP: Ensure proper flow rate settings. Check for air bubbles.")
    print("   ⚠️  Training Required: Yes")
    print("   🔴 Critical Device: Yes")
    print("   ⏰ Max Continuous Use: 8 hours")
    print("   🔧 Maintenance Interval: 30 days")
    
    print("\n3️⃣ Session Initiation:")
    print("   👤 User: admin (IT Department)")
    print("   🕐 Expected Duration: 4 hours")
    print("   🏥 Reason: Post-operative monitoring")
    print("   📍 Location: ICU")

def demo_real_time_tracking():
    """Demonstrate real-time tracking features"""
    print_header("Real-Time Tracking & Monitoring")
    
    print("📍 Location Tracking:")
    print("   - Asset moved from Storage to ICU")
    print("   - GPS/Wi-Fi beacon detection")
    print("   - Location mismatch alerts")
    
    print("\n⏰ Duration Monitoring:")
    print("   - Session start: 14:30")
    print("   - Current duration: 2.5 hours")
    print("   - Remaining time: 1.5 hours")
    print("   - Overuse threshold: 8 hours")
    
    print("\n🚨 Alert System:")
    print("   - Rental expiry warnings")
    print("   - Overuse detection")
    print("   - Inactivity alerts")
    print("   - Location mismatch notifications")

def demo_analytics():
    """Demonstrate analytics and reporting"""
    print_header("Analytics & Reporting Dashboard")
    
    print("📊 Utilization Statistics:")
    print("   - Total Assets: 4")
    print("   - Available: 3")
    print("   - In Use: 1")
    print("   - Utilization Rate: 25%")
    
    print("\n🏥 Department Utilization:")
    print("   - ICU: 45% (High utilization)")
    print("   - ER: 32% (Medium utilization)")
    print("   - Rehab: 18% (Low utilization)")
    print("   - Storage: 5% (Idle assets)")
    
    print("\n💰 Rental ROI Analysis:")
    print("   - Ventilator B: +254% ROI")
    print("   - Infusion Pump C: +50% ROI")
    print("   - Monitor D: -25% ROI (Consider return)")
    
    print("\n🔍 Idle Asset Detection:")
    print("   - Wheelchair D: 45 days idle")
    print("   - Patient Monitor E: 32 days idle")
    print("   - Recommendation: Reallocate or return")

def demo_atlas_of_assets():
    """Demonstrate the AI knowledge layer"""
    print_header("Atlas of Assets - AI Knowledge Layer")
    
    assets = {
        "Infusion Pump": {
            "sop": "Ensure proper flow rate settings. Check for air bubbles. Monitor patient response.",
            "training": "Required",
            "critical": "Yes",
            "max_use": "8 hours",
            "maintenance": "30 days"
        },
        "Ventilator": {
            "sop": "Verify settings match patient requirements. Monitor alarms. Check connections.",
            "training": "Required",
            "critical": "Yes",
            "max_use": "24 hours",
            "maintenance": "15 days"
        },
        "Patient Monitor": {
            "sop": "Calibrate sensors. Verify readings. Check battery status.",
            "training": "Not required",
            "critical": "No",
            "max_use": "12 hours",
            "maintenance": "60 days"
        }
    }
    
    for asset, info in assets.items():
        print(f"\n🔬 {asset}:")
        print(f"   📋 SOP: {info['sop']}")
        print(f"   🎓 Training: {info['training']}")
        print(f"   ⚠️  Critical: {info['critical']}")
        print(f"   ⏰ Max Use: {info['max_use']}")
        print(f"   🔧 Maintenance: {info['maintenance']}")

def demo_workflow_integration():
    """Demonstrate workflow integration points"""
    print_header("Workflow Integration & Extensions")
    
    print("🔗 CMMS Integration:")
    print("   - Asset status synchronization")
    print("   - Maintenance workflow triggers")
    print("   - Inventory management integration")
    
    print("\n📡 IoT Integration:")
    print("   - Real-time location tracking")
    print("   - Sensor data integration")
    print("   - Automated status updates")
    
    print("\n🤝 Vendor Systems:")
    print("   - Rental management integration")
    print("   - Billing system connectivity")
    print("   - Return scheduling automation")
    
    print("\n🔄 Other Workflows:")
    print("   - Repair workflow triggers")
    print("   - Preventive maintenance integration")
    print("   - Training compliance tracking")

def main():
    """Main demo function"""
    print("🏥 Asset Usage & Rental Tracking System - Demo")
    print("🎯 End-to-End Workflow Prototype")
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Demo sections
    demo_asset_scanning()
    demo_real_time_tracking()
    demo_analytics()
    demo_atlas_of_assets()
    demo_workflow_integration()
    
    print_header("Demo Complete")
    print("✅ All features demonstrated successfully!")
    print("\n🚀 To run the actual system:")
    print("   1. python run.py")
    print("   2. Open http://localhost:5000")
    print("   3. Login with: admin / admin123")
    
    print("\n💡 Key Benefits Demonstrated:")
    print("   🎯 Operational Efficiency")
    print("   📉 Cost Reduction")
    print("   🔐 Accountability & Compliance")
    print("   🧠 Smart AI Guidance")
    print("   📊 Informed Decision-Making")

if __name__ == "__main__":
    main() 