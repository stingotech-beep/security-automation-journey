import pandas as pd
import random
from datetime import datetime, timedelta

def generate_fleet(n=500):
    device_types = ['GPS_Tracker', 'Temp_Sensor', 'Barcode_Scanner', 'Fuel_Sensor']
    cities = [
        ('Lagos', 6.5244, 3.3792),
        ('Abuja', 9.0765, 7.3986),
        ('Port Harcourt', 4.8156, 7.0498),
        ('Kano', 12.0022, 8.5920),
        ('Ibadan', 7.3775, 3.9470)
    ]
    
    data = []
    base_time = datetime(2026, 8, 10, 8, 0)
    
    for i in range(n):
        dev_type = random.choice(device_types)
        city, lat, lon = random.choice(cities)
        
        # Normal status
        status = 'ONLINE'
        last_seen = base_time - timedelta(hours=random.randint(0, 12))
        open_ports = 0
        
        # Inject anomalies (5% of devices)
        if random.random() < 0.05:
            anomaly_type = random.choice(['offline', 'impossible_travel', 'open_ports', 'after_hours'])
            
            if anomaly_type == 'offline':
                status = 'OFFLINE'
                last_seen = base_time - timedelta(hours=random.randint(25, 72))
            
            elif anomaly_type == 'impossible_travel':
                # Device was in Lagos 30 mins ago, now in Abuja (impossible)
                pass  # Handled in monitor script via history simulation
            
            elif anomaly_type == 'open_ports':
                open_ports = random.choice([22, 23, 21, 3389])  # SSH, Telnet, FTP, RDP
            
            elif anomaly_type == 'after_hours':
                last_seen = base_time.replace(hour=random.choice([2, 3, 4]))
        
        data.append([
            f"DEV-{1000+i}", dev_type, city, lat, lon, 
            status, last_seen, open_ports
        ])
    
    df = pd.DataFrame(data, columns=[
        'device_id', 'device_type', 'location', 'latitude', 
        'longitude', 'status', 'last_seen', 'open_ports'
    ])
    
    df.to_csv('iot_fleet.csv', index=False)
    print(f"✅ Generated iot_fleet.csv with {n} devices")

if __name__ == "__main__":
    generate_fleet()
