import pandas as pd
import random
from datetime import datetime, timedelta

def generate_alerts(n=1000):
    alert_types = ['Brute Force', 'Malware Detected', 'DDoS Attempt', 
                   'Phishing Email', 'Data Exfiltration', 'Port Scan']
    severities = ['Low', 'Medium', 'High', 'Critical']
    
    # Known bad IPs for simulation
    known_bad_ips = ['192.168.100.55', '10.0.0.99', '172.16.5.200']
    
    data = []
    base_time = datetime(2026, 8, 1, 8, 0)
    
    for i in range(n):
        timestamp = base_time + timedelta(hours=random.randint(0, 720))
        alert_type = random.choice(alert_types)
        
        # Weight severity by alert type
        if alert_type in ['Malware Detected', 'Data Exfiltration']:
            severity = random.choices(severities, weights=[5, 15, 40, 40])[0]
        elif alert_type == 'Brute Force':
            severity = random.choices(severities, weights=[10, 30, 40, 20])[0]
        else:
            severity = random.choices(severities, weights=[40, 35, 20, 5])[0]
        
        source_ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}"
        dest_ip = f"192.168.{random.randint(0,255)}.{random.randint(0,255)}"
        
        # Inject known bad IPs into some alerts
        if random.random() < 0.05:
            source_ip = random.choice(known_bad_ips)
            severity = 'Critical'
        
        data.append([timestamp, f"ALERT-{1000+i}", alert_type, severity, 
                    source_ip, dest_ip, random.randint(1, 100)])
    
    df = pd.DataFrame(data, columns=['timestamp','alert_id','alert_type',
                                     'severity','source_ip','dest_ip','confidence'])
    df.to_csv('soc_alerts.csv', index=False)
    print(f"✅ Generated soc_alerts.csv with {n} alerts")

if __name__ == "__main__":
    generate_alerts()