#!/usr/bin/env python3
"""
Supply Chain IoT Security Monitor v2
SPAA Project: Security + Python + Analytics + Automation

v2 adds: HTML dashboard with fleet health visualizations + security analytics
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from datetime import datetime
import math

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
    """Analyze IoT fleet and generate security dashboard."""
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path)
    df['last_seen'] = pd.to_datetime(df['last_seen'])
    df['hour'] = df['last_seen'].dt.hour

    now = datetime(2026, 8, 10, 20, 0)
    offline_threshold = now - pd.Timedelta(hours=24)

    total = len(df)
    online = len(df[df['status'] == 'ONLINE'])
    offline = len(df[df['status'] == 'OFFLINE'])

    # Security flags
    exposed = df[df['open_ports'] != 0].copy()
    exposed['port_service'] = exposed['open_ports'].map(CRITICAL_PORTS).fillna('Unknown')

    after_hours = df[(df['hour'] >= 2) & (df['hour'] <= 5)]

    # Fleet health
    healthy = len(df[(df['status'] == 'ONLINE') & (df['open_ports'] == 0) & 
                     (~df['device_id'].isin(after_hours['device_id']))])
    health_pct = (healthy / total) * 100 if total > 0 else 0

    print(f"\nTotal fleet devices: {total}")
    print(f"Online: {online} | Offline: {offline}")
    print(f"Exposed ports: {len(exposed)}")
    print(f"After-hours activity: {len(after_hours)}")
    print(f"Fleet health: {health_pct:.1f}%")

    # Charts
    charts = generate_charts(df, exposed, after_hours, offline, online)

    # HTML
    report_file = build_html(df, exposed, after_hours, charts, total, online, offline, 
                             len(exposed), len(after_hours), health_pct)
    print(f"\n✅ Dashboard generated: {report_file}")

    return df

def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return b64

def generate_charts(df, exposed, after_hours, offline, online):
    charts = {}

    # Chart 1: Fleet status pie
    fig, ax = plt.subplots()
    labels = ['Online', 'Offline']
    sizes = [online, offline]
    colors = ['#43a047', '#e53935']
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax.set_title('Fleet Status Distribution')
    charts['status'] = fig_to_base64(fig)

    # Chart 2: Exposed ports breakdown
    if not exposed.empty:
        fig, ax = plt.subplots()
        port_counts = exposed['port_service'].value_counts()
        port_counts.plot(kind='bar', ax=ax, color='indianred')
        ax.set_title('Exposed Ports by Service')
        ax.set_xlabel('Service')
        ax.set_ylabel('Device Count')
        ax.tick_params(axis='x', rotation=0)
        charts['ports'] = fig_to_base64(fig)

    # Chart 3: Device types at risk
    fig, ax = plt.subplots()
    risk_df = df[(df['status'] == 'OFFLINE') | (df['open_ports'] != 0)]
    if not risk_df.empty:
        risk_df['device_type'].value_counts().plot(kind='barh', ax=ax, color='steelblue')
        ax.set_title('At-Risk Device Types')
        ax.set_xlabel('Count')
        charts['types'] = fig_to_base64(fig)

    # Chart 4: Activity by hour (heatmap-style)
    fig, ax = plt.subplots()
    hourly = df['hour'].value_counts().sort_index()
    colors_hour = ['#e53935' if h in [2,3,4,5] else '#43a047' for h in hourly.index]
    ax.bar(hourly.index, hourly.values, color=colors_hour)
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Device Activity')
    ax.set_title('Fleet Activity by Hour (Red = After-Hours Risk)')
    charts['hourly'] = fig_to_base64(fig)

    return charts

def build_html(df, exposed, after_hours, charts, total, online, offline, exposed_count, after_count, health_pct):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"IoT_Fleet_Dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    # Exposed devices table
    exposed_html = exposed[['device_id', 'device_type', 'location', 'open_ports', 'port_service']].head(10).to_html(
        index=False, classes='table table-critical') if not exposed.empty else "<p>No exposed ports detected.</p>"

    chart_html = ""
    for name, b64 in charts.items():
        chart_html += f'<h3>{name.replace("_", " ").title()}</h3><img src="data:image/png;base64,{b64}" style="max-width:100%;height:auto;"><br><br>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Supply Chain IoT Fleet Dashboard</title>
<style>
body{{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;max-width:1000px;margin:40px auto;padding:20px;background:#f5f7fa;color:#333}}
.container{{background:#fff;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
h1{{color:#1a237e;border-bottom:3px solid #3949ab;padding-bottom:10px}}
h2{{color:#3949ab;margin-top:25px}}
h3{{color:#555;margin-top:18px;font-size:1em}}
.stat-box{{display:inline-block;background:#e8eaf6;padding:15px 25px;margin:8px;border-radius:6px;text-align:center;min-width:120px}}
.stat-box strong{{display:block;font-size:1.6em;color:#1a237e}}
.health-good{{background:#e8f5e9!important}}
.health-bad{{background:#ffebee!important}}
.table{{border-collapse:collapse;width:100%;margin-top:10px;font-size:0.9em}}
.table th,.table td{{border:1px solid #ddd;padding:8px;text-align:left}}
.table th{{background:#3949ab;color:#fff}}
.table tr:nth-child(even){{background:#f9f9f9}}
.table-critical td{{background:#ffebee!important;color:#c62828;font-weight:bold}}
img{{border:1px solid #ddd;border-radius:4px;padding:5px;background:#fff;max-width:100%}}
.footer{{margin-top:30px;color:#999;font-size:0.85em;border-top:1px solid #ddd;padding-top:14px;text-align:center}}
</style>
</head>
<body>
<div class="container">
<h1>🚛 Supply Chain IoT Fleet Dashboard</h1>
<p style="color:#777">Generated: {timestamp}</p>

<div>
  <div class="stat-box"><strong>{total}</strong>Total Devices</div>
  <div class="stat-box"><strong>{online}</strong>Online</div>
  <div class="stat-box"><strong>{offline}</strong>Offline</div>
  <div class="stat-box"><strong>{exposed_count}</strong>Exposed Ports</div>
  <div class="stat-box"><strong>{after_count}</strong>After-Hours</div>
  <div class="stat-box {'health-good' if health_pct >= 80 else 'health-bad'}"><strong>{health_pct:.1f}%</strong>Health Score</div>
</div>

<h2>🚨 Devices with Exposed Ports</h2>
{exposed_html}

<h2>📊 Visualizations</h2>
{chart_html}

<div class="footer">
Supply Chain IoT Monitor v2 | Automated by SPAA<br>
Python + Pandas + Matplotlib | Fleet Security Pipeline
</div>
</div>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

if __name__ == "__main__":
    import os
    CSV_FILE = 'iot_fleet.csv'
    if not os.path.exists(CSV_FILE):
        print(f"⚠️  File not found: {CSV_FILE}")
        print("Run generate_iot_fleet.py first to create sample data.")
    else:
        analyze_fleet(CSV_FILE)