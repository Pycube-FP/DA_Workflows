#!/usr/bin/env python3
"""
RFID Simulator for Asset Tracking System
This simulates RFID readers detecting asset movements
"""

import requests
import time
import random
from datetime import datetime
import json

BASE_URL = "http://localhost:5000"

# Simulated RFID readers
RFID_READERS = {
    "Storage": {"x": 100, "y": 100},
    "ICU": {"x": 200, "y": 150},
    "ER": {"x": 300, "y": 200},
    "OR": {"x": 250, "y": 300},
    "Rehab": {"x": 150, "y": 250}
}

# Sample assets
ASSETS = [
    {"id": "INF001", "name": "Infusion Pump A", "category": "infusion_pump"},
    {"id": "VENT001", "name": "Ventilator B", "category": "ventilator"},
    {"id": "MON001", "name": "Patient Monitor C", "category": "monitor"},
    {"id": "WC001", "name": "Wheelchair D", "category": "wheelchair"}
]

def send_rfid_event(asset_id, location, event_type):
    """Send RFID event to the system"""
    timestamp = datetime.now().isoformat()
    
    data = {
        "asset_id": asset_id,
        "location": location,
        "event_type": event_type,  # 'enter' or 'exit'
        "timestamp": timestamp
    }
    
    try:
        response = requests.post(f"{BASE_URL}/rfid_event", json=data)
        if response.status_code == 200:
            print(f"✅ RFID Event: {asset_id} {event_type} {location}")
        else:
            print(f"❌ RFID Event Failed: {response.text}")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to system at {BASE_URL}")
        return False
    
    return True

def simulate_asset_movement():
    """Simulate realistic asset movements"""
    print("🏥 RFID Asset Tracking Simulator")
    print("=" * 50)
    print("Simulating automatic session creation via RFID...")
    print()
    
    # Start with all assets in Storage
    asset_locations = {asset["id"]: "Storage" for asset in ASSETS}
    
    # Simulate movements
    movements = [
        # Infusion pump goes to ICU
        ("INF001", "Storage", "ICU"),
        # Ventilator goes to ER
        ("VENT001", "Storage", "ER"),
        # Monitor goes to OR
        ("MON001", "Storage", "OR"),
        # Wheelchair goes to Rehab
        ("WC001", "Storage", "Rehab"),
        
        # Some assets return to Storage
        ("INF001", "ICU", "Storage"),
        ("MON001", "OR", "Storage"),
        
        # New movements
        ("INF001", "Storage", "ER"),
        ("MON001", "Storage", "ICU"),
    ]
    
    for i, (asset_id, from_location, to_location) in enumerate(movements):
        print(f"🔄 Movement {i+1}: {asset_id} from {from_location} to {to_location}")
        
        # Send exit event from current location
        if from_location != "Storage":
            send_rfid_event(asset_id, from_location, "exit")
            time.sleep(1)
        
        # Send enter event to new location
        send_rfid_event(asset_id, to_location, "enter")
        
        # Update location
        asset_locations[asset_id] = to_location
        
        print(f"   📍 {asset_id} now in {to_location}")
        print()
        time.sleep(2)
    
    print("✅ RFID simulation completed!")
    print("\n📊 Check the dashboard to see automatic session creation:")
    print(f"   {BASE_URL}/dashboard")

def simulate_realtime_tracking():
    """Simulate real-time RFID tracking"""
    print("🔄 Real-time RFID Tracking Simulation")
    print("=" * 50)
    print("Press Ctrl+C to stop...")
    print()
    
    try:
        while True:
            # Randomly select an asset and movement
            asset = random.choice(ASSETS)
            from_location = random.choice(list(RFID_READERS.keys()))
            to_location = random.choice(list(RFID_READERS.keys()))
            
            if from_location != to_location:
                print(f"🔄 {asset['id']} moving from {from_location} to {to_location}")
                
                # Send RFID events
                send_rfid_event(asset['id'], from_location, "exit")
                time.sleep(0.5)
                send_rfid_event(asset['id'], to_location, "enter")
                
                print(f"   📍 {asset['id']} now in {to_location}")
                print()
            
            time.sleep(random.randint(3, 8))  # Random interval
            
    except KeyboardInterrupt:
        print("\n👋 RFID simulation stopped")

def main():
    """Main function"""
    print("🏥 RFID Asset Tracking Simulator")
    print("=" * 50)
    print("1. Simulate asset movements")
    print("2. Real-time tracking simulation")
    print("3. Exit")
    print()
    
    choice = input("Select option (1-3): ")
    
    if choice == "1":
        simulate_asset_movement()
    elif choice == "2":
        simulate_realtime_tracking()
    elif choice == "3":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")

if __name__ == "__main__":
    main() 