#!/usr/bin/env python3
"""
Healthcare HIPAA Auditor v2
SPAA Project: Security + Python + Analytics + Automation

v2 adds: HTML dashboard with compliance visualizations + violation analysis
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from datetime import datetime

def audit_hipaa(csv_path: str):
    """Analyze access logs and generate compliance dashboard."""
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['date'] = df['timestamp'].dt.date

    now = df['timestamp'].max()
    offline_threshold = now - pd.Timedelta(hours=24)

    total = len(df)
    unique_users = df['user_id'].nunique()

    # Violation detection
    after_hours = df[(df['hour'] < 6) | (df['hour'] >= 22)]
    cross_dept = df[(df['role'] == 'Admin') & 
                    (df['department'] == 'Billing') & 
                    (df['action'].isin(['VIEW', 'EDIT']))]

    daily_counts = df.groupby(['date', 'user_id']).size().reset_index(name='count')
    bulk = daily_counts[daily_counts['count'] > 15]

    # Compliance score
    total_violations = len(after_hours) + len(cross_dept) + len(bulk)
    compliance_score = max(0, 100 - (total_violations / total * 100))

    print(f"\nTotal access events: {total}")
    print(f"After-hours violations: {len(after_hours)}")
    print(f"Cross-dept violations: {len(cross_dept)}")
    print(f"Bulk access violations: {len(bulk)}")
    print(f"Compliance score: {compliance_score:.1f}%")

    # Generate charts
    charts = generate_charts(df, after_hours, cross_dept, bulk)

    # Build HTML
    report_file = build_html(df, after_hours, cross_dept, bulk, charts, total, unique_users, compliance_score)
    print(f"\n✅ Dashboard generated: {report_file}")

    return df

def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return b64

def generate_charts(df, after_hours, cross_dept, bulk):
    charts = {}

    # Chart 1: Violations by type
    fig, ax = plt.subplots()
    violation_types = ['After-Hours', 'Cross-Dept', 'Bulk Access']
    counts = [len(after_hours), len(cross_dept), len(bulk)]
    colors = ['#e53935', '#fb8c00', '#fdd835']
    ax.bar(violation_types, counts, color=colors)
    ax.set_title('HIPAA Violations by Type')
    ax.set_ylabel('Count')
    charts['violations'] = fig_to_base64(fig)

    # Chart 2: Access by hour (heatmap-style bar)
    fig, ax = plt.subplots()
    hourly = df['hour'].value_counts().sort_index()
    ax.bar(hourly.index, hourly.values, color='steelblue')
    ax.axvline(6, color='red', linestyle='--', label='After-hours start')
    ax.axvline(22, color='red', linestyle='--', label='After-hours end')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Access Events')
    ax.set_title('Access Patterns (Red = After-Hours Zone)')
    ax.legend()
    charts['hourly'] = fig_to_base64(fig)

    # Chart 3: Violations by role
    fig, ax = plt.subplots()
    role_violations = pd.concat([
        after_hours['role'],
        cross_dept['role']
    ]).value_counts()
    if not role_violations.empty:
        role_violations.plot(kind='pie', ax=ax, autopct='%1.1f%%')
        ax.set_title('Violations by Role')
        ax.set_ylabel('')
    charts['roles'] = fig_to_base64(fig)

    # Chart 4: Daily access trend
    fig, ax = plt.subplots()
    daily = df.groupby('date').size()
    ax.plot(daily.index, daily.values, marker='o', color='#3949ab')
    ax.set_xlabel('Date')
    ax.set_ylabel('Access Events')
    ax.set_title('Daily Access Volume')
    ax.tick_params(axis='x', rotation=45)
    charts['daily'] = fig_to_base64(fig)

    return charts

def build_html(df, after_hours, cross_dept, bulk, charts, total, unique_users, compliance_score):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"HIPAA_Dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    # Top violations table
    top_violations = after_hours.head(5)[['timestamp', 'user_id', 'role', 'patient_id', 'hour']].copy()
    top_violations['violation_type'] = 'After-Hours'

    if not cross_dept.empty:
        cd = cross_dept.head(5)[['timestamp', 'user_id', 'role', 'patient_id']].copy()
        cd['hour'] = cd['timestamp'].dt.hour
        cd['violation_type'] = 'Cross-Dept'
        top_violations = pd.concat([top_violations, cd])

    violations_html = top_violations.to_html(index=False, classes='table table-critical') if not top_violations.empty else "<p>No violations detected.</p>"

    chart_html = ""
    for name, b64 in charts.items():
        chart_html += f'<h3>{name.replace("_", " ").title()}</h3><img src="data:image/png;base64,{b64}" style="max-width:100%;height:auto;"><br><br>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Healthcare HIPAA Compliance Dashboard</title>
<style>
body{{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;max-width:1000px;margin:40px auto;padding:20px;background:#f5f7fa;color:#333}}
.container{{background:#fff;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
h1{{color:#1a237e;border-bottom:3px solid #3949ab;padding-bottom:10px}}
h2{{color:#3949ab;margin-top:25px}}
h3{{color:#555;margin-top:18px;font-size:1em}}
.stat-box{{display:inline-block;background:#e8eaf6;padding:15px 25px;margin:8px;border-radius:6px;text-align:center;min-width:120px}}
.stat-box strong{{display:block;font-size:1.6em;color:#1a237e}}
.compliance-good{{background:#e8f5e9!important}}
.compliance-bad{{background:#ffebee!important}}
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
<h1>🏥 Healthcare HIPAA Compliance Dashboard</h1>
<p style="color:#777">Generated: {timestamp}</p>

<div>
  <div class="stat-box"><strong>{total}</strong>Total Events</div>
  <div class="stat-box"><strong>{unique_users}</strong>Unique Users</div>
  <div class="stat-box"><strong>{len(after_hours)}</strong>After-Hours</div>
  <div class="stat-box"><strong>{len(cross_dept)}</strong>Cross-Dept</div>
  <div class="stat-box"><strong>{len(bulk)}</strong>Bulk Access</div>
  <div class="stat-box {'compliance-good' if compliance_score >= 80 else 'compliance-bad'}"><strong>{compliance_score:.1f}%</strong>Compliance</div>
</div>

<h2>🚨 Top Violations</h2>
{violations_html}

<h2>📊 Visualizations</h2>
{chart_html}

<div class="footer">
Healthcare HIPAA Auditor v2 | Automated by SPAA<br>
Python + Pandas + Matplotlib | Compliance Monitoring Pipeline
</div>
</div>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

if __name__ == "__main__":
    import os
    CSV_FILE = 'healthcare_access_logs.csv'
    if not os.path.exists(CSV_FILE):
        print(f"⚠️  File not found: {CSV_FILE}")
        print("Run generate_sample_logs.py first to create sample data.")
    else:
        audit_hipaa(CSV_FILE)