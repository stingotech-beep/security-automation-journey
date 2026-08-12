#!/usr/bin/env python3
"""
SOC Alert Triage Bot v1
SPAA Project: Security + Python + Analytics + Automation

Automated SIEM alert triage with risk scoring and auto-response.
"""

import pandas as pd
from datetime import datetime

# Simulated Threat Intelligence Database
THREAT_INTEL = {
    '192.168.100.55': {'reputation': 'Malicious', 'category': 'C2 Server'},
    '10.0.0.99': {'reputation': 'Suspicious', 'category': 'Tor Exit Node'},
    '172.16.5.200': {'reputation': 'Malicious', 'category': 'Known Botnet'}
}

def check_ip_reputation(ip):
    """Simulated threat intel lookup."""
    return THREAT_INTEL.get(ip, {'reputation': 'Unknown', 'category': 'N/A'})

def calculate_risk_score(row):
    """AI-like risk scoring based on multiple signals."""
    score = 0
    
    # Base severity score
    severity_scores = {'Low': 10, 'Medium': 30, 'High': 60, 'Critical': 90}
    score += severity_scores.get(row['severity'], 0)
    
    # Threat intel enrichment
    intel = check_ip_reputation(row['source_ip'])
    if intel['reputation'] == 'Malicious':
        score += 50
    elif intel['reputation'] == 'Suspicious':
        score += 25
    
    # Alert type risk
    high_risk_types = ['Malware Detected', 'Data Exfiltration', 'Brute Force']
    if row['alert_type'] in high_risk_types:
        score += 15
    
    # Confidence adjustment
    if row['confidence'] < 30:
        score -= 20  # Likely false positive
    
    return min(score, 100)

def triage_alerts(csv_path: str):
    """Main triage engine."""
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    print(f"\nTotal alerts: {len(df)}")
    print(f"Severity breakdown:")
    print(df['severity'].value_counts())
    
    # AI Risk Scoring
    print("\n🧠 Running AI risk analysis...")
    df['risk_score'] = df.apply(calculate_risk_score, axis=1)
    
    # Enrich with threat intel
    df['ip_reputation'] = df['source_ip'].apply(
        lambda x: check_ip_reputation(x)['reputation']
    )
    
    # Triage Decision Engine
    def triage_decision(row):
        if row['risk_score'] < 20:
            return 'AUTO-CLOSE'
        elif row['risk_score'] < 50:
            return 'MONITOR'
        elif row['risk_score'] < 75:
            return 'ESCALATE'
        else:
            return 'CRITICAL - IMMEDIATE ACTION'
    
    df['action'] = df.apply(triage_decision, axis=1)
    
    # Results
    print(f"\n{'='*60}")
    print("TRIAGE RESULTS")
    print(f"{'='*60}")
    
    action_counts = df['action'].value_counts()
    for action, count in action_counts.items():
        print(f"{action}: {count} alerts")
    
    # Critical alerts detail
    critical = df[df['action'] == 'CRITICAL - IMMEDIATE ACTION']
    print(f"\n🚨 CRITICAL ALERTS ({len(critical)}):")
    if len(critical) > 0:
        print(critical[['timestamp','alert_id','alert_type','source_ip',
                       'risk_score']].to_string(index=False))
    
    # Export triaged results
    df.to_csv('triaged_alerts.csv', index=False)
    print(f"\n✅ Exported to triaged_alerts.csv")
    
    # Auto-close summary
    auto_closed = len(df[df['action'] == 'AUTO-CLOSE'])
    print(f"\n💡 Automation saved {auto_closed} manual reviews ({auto_closed/len(df)*100:.1f}%)")
    
    return df

if __name__ == "__main__":
    CSV_FILE = 'soc_alerts.csv'
    
    try:
        import os
        if not os.path.exists(CSV_FILE):
            print("Alert data not found. Generating...")
            import generate_soc_alerts
            generate_soc_alerts.generate_alerts()
        
        triage_alerts(CSV_FILE)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
