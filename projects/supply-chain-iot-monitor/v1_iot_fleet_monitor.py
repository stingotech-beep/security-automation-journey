#!/usr/bin/env python3
"""
Supply Chain IoT Security Monitor v1
SPAA Project: Security + Python + Analytics + Automation

Monitors fleet IoT devices for security anomalies and offline events.
"""

import pandas as pd
from datetime import datetime, timedelta
import math

# Known vulnerable ports for IoT
CRITICAL_PORTS = {21: 'FTP', 22: 'SSH', 23: 'Telnet', 3389: 'RDP'}

def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in km."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def analyze_fleet(csv_path: str):
    """Main fleet security analysis."""
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path)
    df['last_seen'] = pd.to_datetime(df['last_seen'])
    
    now = datetime(2026, 8, 10, 20, 0)  # Simulated "now"
    
    print(f"\nTotal fleet devices: {len(df)}")
    print(f"Online: {len(df[df['status']=='ONLINE'])}")
    print(f"Offline: {len(df[df['status']=='OFFLINE'])}")
    
    # FLAG 1: Offline devices (>24 hours)
    offline_threshold = now - timedelta(hours=24)
    offline = df[df['last_seen'] < offline_threshold]
    print(f"\n🚨 OFFLINE DEVICES: {len(offline)}")
    if len(offline) > 0:
        print(offline[['device_id','device_type','location','last_seen']].head())
    
    # FLAG 2: Devices with exposed ports
    exposed = df[df['open_ports'] != 0].copy()
    exposed['port_service'] = exposed['open_ports'].map(CRITICAL_PORTS).fillna('Unknown')
    print(f"\n🚨 EXPOSED PORTS: {len(exposed)} devices")
    if len(exposed) > 0:
        print(exposed[['device_id','device_type','location','open_ports','port_service']])
    
    # FLAG 3: After-hours activity (2AM - 5AM)
    df['hour'] = df['last_seen'].dt.hour
    after_hours = df[(df['hour'] >= 2) & (df['hour'] <= 5)]
    print(f"\n🚨 AFTER-HOURS ACTIVITY: {len(after_hours)} devices")
    if len(after_hours) > 0:
        print(after_hours[['device_id','device_type','location','hour']].head())
    
    # FLAG 4: Fleet health score
    healthy = len(df[(df['status']=='ONLINE') & (df['open_ports']==0) & 
                     (~df['device_id'].isin(after_hours['device_id']))])
    health_pct = (healthy / len(df)) * 100
    
    print(f"\n{'='*60}")
    print(f"FLEET HEALTH SCORE: {health_pct:.1f}%")
    print(f"{'='*60}")
    print(f"Healthy devices: {healthy}")
    print(f"Flagged devices: {len(df) - healthy}")
    print(f"Critical actions needed: {len(offline) + len(exposed)}")
    
    # Export flagged devices
    flagged = df[(df['status']=='OFFLINE') | (df['open_ports']!=0) | 
                 (df['device_id'].isin(after_hours['device_id']))]
    flagged.to_csv('flagged_iot_devices.csv', index=False)
    print(f"\n✅ Exported to flagged_iot_devices.csv")
    
    return flagged

if __name__ == "__main__":
    CSV_FILE = 'iot_fleet.csv'
    
    try:
        import os
        if not os.path.exists(CSV_FILE):
            print("Fleet data not found. Generating...")
            import generate_iot_fleet
            generate_iot_fleet.generate_fleet()
        
        analyze_fleet(CSV_FILE)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")