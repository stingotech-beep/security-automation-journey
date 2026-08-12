#!/usr/bin/env python3
"""
Government NIST 800-53 Compliance Mapper v2
SPAA Project: Security + Python + Analytics + Automation

v2 adds: HTML dashboard with compliance visualizations + audit analytics
"""

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from datetime import datetime

def map_compliance(csv_path: str):
    """Analyze NIST compliance and generate audit dashboard."""
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path)

    total = len(df)
    unique_systems = df['hostname'].nunique()

    # Status breakdown
    pass_count = len(df[df['status'] == 'Pass'])
    fail_count = len(df[df['status'] == 'Fail'])
    partial_count = len(df[df['status'] == 'Partial'])
    compliance_pct = (pass_count / total) * 100 if total > 0 else 0

    # Critical failures
    critical = df[(df['status'] == 'Fail') & (df['severity'] == 'Critical')]

    # Control analysis
    control_summary = df.groupby(['control_id', 'control_name', 'status']).size().unstack(fill_value=0)

    print(f"\nTotal controls checked: {total}")
    print(f"Unique systems: {unique_systems}")
    print(f"Pass: {pass_count} | Fail: {fail_count} | Partial: {partial_count}")
    print(f"Compliance: {compliance_pct:.1f}%")
    print(f"Critical failures: {len(critical)}")

    # Charts
    charts = generate_charts(df, control_summary, pass_count, fail_count, partial_count)

    # HTML
    report_file = build_html(df, critical, control_summary, charts, total, unique_systems,
                             pass_count, fail_count, partial_count, compliance_pct)
    print(f"\n✅ Dashboard generated: {report_file}")

    return df

def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return b64

def generate_charts(df, control_summary, pass_count, fail_count, partial_count):
    charts = {}

    # Chart 1: Overall compliance pie
    fig, ax = plt.subplots()
    labels = ['Pass', 'Fail', 'Partial']
    sizes = [pass_count, fail_count, partial_count]
    colors = ['#43a047', '#e53935', '#fdd835']
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
    ax.set_title('NIST 800-53 Compliance Overview')
    charts['compliance'] = fig_to_base64(fig)

    # Chart 2: Control pass/fail stacked bar
    if not control_summary.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        control_summary.plot(kind='barh', stacked=True, ax=ax, 
                           color={'Pass': '#43a047', 'Fail': '#e53935', 'Partial': '#fdd835'})
        ax.set_title('Control Compliance by NIST ID')
        ax.set_xlabel('Count')
        charts['controls'] = fig_to_base64(fig)

    # Chart 3: Score distribution
    fig, ax = plt.subplots()
    df['score'].hist(bins=20, ax=ax, color='steelblue', edgecolor='white')
    ax.axvline(df['score'].mean(), color='red', linestyle='--', label=f'Mean: {df["score"].mean():.1f}')
    ax.set_xlabel('Control Score')
    ax.set_ylabel('Frequency')
    ax.set_title('Score Distribution Across All Controls')
    ax.legend()
    charts['scores'] = fig_to_base64(fig)

    # Chart 4: Severity breakdown of failures
    failures = df[df['status'] == 'Fail']
    if not failures.empty:
        fig, ax = plt.subplots()
        failures['severity'].value_counts().plot(kind='bar', ax=ax, color='indianred')
        ax.set_title('Failure Severity Breakdown')
        ax.set_xlabel('Severity')
        ax.set_ylabel('Count')
        ax.tick_params(axis='x', rotation=0)
        charts['severity'] = fig_to_base64(fig)

    return charts

def build_html(df, critical, control_summary, charts, total, unique_systems,
               pass_count, fail_count, partial_count, compliance_pct):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"NIST_Dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    # Critical failures table
    critical_html = critical[['hostname', 'control_id', 'control_name', 'score']].head(10).to_html(
        index=False, classes='table table-critical') if not critical.empty else "<p>No critical failures.</p>"

    # Control summary table
    control_html = control_summary.reset_index().to_html(classes='table', index=False) if not control_summary.empty else "<p>No control data.</p>"

    chart_html = ""
    for name, b64 in charts.items():
        chart_html += f'<h3>{name.replace("_", " ").title()}</h3><img src="data:image/png;base64,{b64}" style="max-width:100%;height:auto;"><br><br>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Government NIST 800-53 Compliance Dashboard</title>
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
<h1>🏛️ NIST 800-53 Compliance Dashboard</h1>
<p style="color:#777">Generated: {timestamp}</p>

<div>
  <div class="stat-box"><strong>{total}</strong>Controls Checked</div>
  <div class="stat-box"><strong>{unique_systems}</strong>Systems</div>
  <div class="stat-box"><strong>{pass_count}</strong>Pass</div>
  <div class="stat-box"><strong>{fail_count}</strong>Fail</div>
  <div class="stat-box"><strong>{partial_count}</strong>Partial</div>
  <div class="stat-box {'compliance-good' if compliance_pct >= 80 else 'compliance-bad'}"><strong>{compliance_pct:.1f}%</strong>Compliance</div>
</div>

<h2>🚨 Critical Failures</h2>
{critical_html}

<h2>📊 Visualizations</h2>
{chart_html}

<h2>📋 Control Summary</h2>
{control_html}

<div class="footer">
NIST 800-53 Compliance Mapper v2 | Automated by SPAA<br>
Python + Pandas + Matplotlib | Government Audit Pipeline
</div>
</div>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

if __name__ == "__main__":
    import os
    CSV_FILE = 'system_configs.csv'
    if not os.path.exists(CSV_FILE):
        print(f"⚠️  File not found: {CSV_FILE}")
        print("Run generate_system_configs.py first to create sample data.")
    else:
        map_compliance(CSV_FILE)