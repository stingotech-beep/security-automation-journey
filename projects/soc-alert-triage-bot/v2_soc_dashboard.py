#!/usr/bin/env python3
"""
SOC Alert Triage Bot v2
SPAA Project: Security + Python + Analytics + Automation

v2 adds: HTML dashboard with charts + auto-export
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from datetime import datetime

# Threat Intel
THREAT_INTEL = {
    '192.168.100.55': {'reputation': 'Malicious', 'category': 'C2 Server'},
    '10.0.0.99': {'reputation': 'Suspicious', 'category': 'Tor Exit Node'},
    '172.16.5.200': {'reputation': 'Malicious', 'category': 'Known Botnet'}
}

CRITICAL_PORTS = {21: 'FTP', 22: 'SSH', 23: 'Telnet', 3389: 'RDP'}

def check_ip_reputation(ip):
    return THREAT_INTEL.get(ip, {'reputation': 'Unknown', 'category': 'N/A'})

def calculate_risk_score(row):
    score = 0
    severity_scores = {'Low': 10, 'Medium': 30, 'High': 60, 'Critical': 90}
    score += severity_scores.get(row['severity'], 0)
    
    intel = check_ip_reputation(row['source_ip'])
    if intel['reputation'] == 'Malicious':
        score += 50
    elif intel['reputation'] == 'Suspicious':
        score += 25
    
    high_risk = ['Malware Detected', 'Data Exfiltration', 'Brute Force']
    if row['alert_type'] in high_risk:
        score += 15
    
    if row['confidence'] < 30:
        score -= 20
    
    return min(score, 100)

def triage_alerts(csv_path: str):
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Risk scoring
    df['risk_score'] = df.apply(calculate_risk_score, axis=1)
    df['ip_reputation'] = df['source_ip'].apply(
        lambda x: check_ip_reputation(x)['reputation']
    )
    
    def triage_decision(row):
        if row['risk_score'] < 20:
            return 'AUTO-CLOSE'
        elif row['risk_score'] < 50:
            return 'MONITOR'
        elif row['risk_score'] < 75:
            return 'ESCALATE'
        else:
            return 'CRITICAL'
    
    df['action'] = df.apply(triage_decision, axis=1)
    
    # Stats
    total = len(df)
    action_counts = df['action'].value_counts()
    critical = df[df['action'] == 'CRITICAL']
    auto_closed = len(df[df['action'] == 'AUTO-CLOSE'])
    
    print(f"\nTotal alerts: {total}")
    print(f"Critical: {len(critical)}")
    print(f"Auto-closed: {auto_closed}")
    
    # Generate charts
    charts = generate_charts(df, action_counts)
    
    # Build HTML
    report_file = build_html(df, critical, action_counts, charts, total, auto_closed)
    print(f"\n✅ Dashboard generated: {report_file}")
    
    df.to_csv('triaged_alerts.csv', index=False)
    return df

def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return b64

def generate_charts(df, action_counts):
    charts = {}
    
    # Chart 1: Action distribution (pie)
    fig, ax = plt.subplots()
    colors = {'AUTO-CLOSE': '#43a047', 'MONITOR': '#fb8c00', 
              'ESCALATE': '#e53935', 'CRITICAL': '#b71c1c'}
    bar_colors = [colors.get(a, 'gray') for a in action_counts.index]
    action_counts.plot(kind='bar', ax=ax, color=bar_colors)
    ax.set_title('Alert Triage Actions')
    ax.set_xlabel('Action')
    ax.set_ylabel('Count')
    ax.tick_params(axis='x', rotation=0)
    charts['actions'] = fig_to_base64(fig)
    
    # Chart 2: Severity breakdown
    fig, ax = plt.subplots()
    df['severity'].value_counts().plot(kind='pie', ax=ax, autopct='%1.1f%%')
    ax.set_title('Alert Severity Distribution')
    ax.set_ylabel('')
    charts['severity'] = fig_to_base64(fig)
    
    # Chart 3: Top alert types
    fig, ax = plt.subplots()
    df['alert_type'].value_counts().head(6).plot(kind='barh', ax=ax, color='steelblue')
    ax.set_title('Top Alert Types')
    charts['types'] = fig_to_base64(fig)
    
    return charts

def build_html(df, critical, action_counts, charts, total, auto_closed):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"SOC_Dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    
    action_html = action_counts.to_frame().to_html(classes='table', header=False)
    
    critical_html = critical[['timestamp','alert_id','alert_type','source_ip','risk_score']].head(10).to_html(index=False, classes='table table-critical') if not critical.empty else "<p>No critical alerts.</p>"
    
    chart_html = ""
    for name, b64 in charts.items():
        chart_html += f'<h3>{name.title()} Chart</h3><img src="data:image/png;base64,{b64}" style="max-width:100%;"><br><br>'
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>SOC Alert Dashboard</title>
<style>
body{{font-family:Segoe UI,sans-serif;max-width:1000px;margin:40px auto;padding:20px;background:#f5f7fa;color:#333}}
.container{{background:#fff;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
h1{{color:#1a237e;border-bottom:3px solid #3949ab;padding-bottom:10px}}
.stat-box{{display:inline-block;background:#e8eaf6;padding:15px 25px;margin:8px;border-radius:6px;text-align:center;min-width:120px}}
.stat-box strong{{display:block;font-size:1.6em;color:#1a237e}}
.table{{border-collapse:collapse;width:100%;margin-top:10px;font-size:0.9em}}
.table th,.table td{{border:1px solid #ddd;padding:8px;text-align:left}}
.table th{{background:#3949ab;color:#fff}}
.table tr:nth-child(even){{background:#f9f9f9}}
.table-critical td{{background:#ffebee!important;color:#c62828;font-weight:bold}}
img{{border:1px solid #ddd;border-radius:4px;padding:5px;background:#fff}}
.footer{{margin-top:30px;color:#999;font-size:0.85em;border-top:1px solid #ddd;padding-top:14px;text-align:center}}
</style></head>
<body>
<div class="container">
<h1>🛡️ SOC Alert Triage Dashboard</h1>
<p style="color:#777">Generated: {timestamp}</p>
<div>
  <div class="stat-box"><strong>{total}</strong>Total Alerts</div>
  <div class="stat-box"><strong>{len(critical)}</strong>Critical</div>
  <div class="stat-box"><strong>{auto_closed}</strong>Auto-Closed</div>
  <div class="stat-box"><strong>{(auto_closed/total*100):.1f}%</strong>Time Saved</div>
</div>

<h2>🚨 Top Critical Alerts</h2>
{critical_html}

<h2>📊 Visualizations</h2>
{chart_html}

<h2>📋 Action Summary</h2>
{action_html}

<div class="footer">
SOC Alert Triage Bot v2 | Automated by SPAA<br>
Python + Pandas + Matplotlib | Security Operations Center Pipeline
</div>
</div></body></html>"""
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

if __name__ == "__main__":
    import os
    CSV_FILE = 'soc_alerts.csv'
    if not os.path.exists(CSV_FILE):
        import generate_soc_alerts
        generate_soc_alerts.generate_alerts()
    triage_alerts(CSV_FILE)