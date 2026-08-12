#!/usr/bin/env python3
"""
Fintech Fraud Detector v2
SPAA Project: Security + Python + Analytics + Automation

v2 adds: HTML dashboard with fraud visualizations + risk profiling
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from datetime import datetime

def analyze_fraud(csv_path: str):
    """Load transaction data, detect anomalies, generate dashboard."""
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path)

    print(f"\nTotal transactions: {len(df):,}")
    print(f"Columns: {list(df.columns)}")

    # Identify fraud column
    fraud_col = 'Class' if 'Class' in df.columns else None
    if fraud_col:
        fraud_count = df[fraud_col].sum()
        fraud_pct = (fraud_count / len(df)) * 100
        print(f"Fraud cases: {fraud_count}")
        print(f"Fraud percentage: {fraud_pct:.4f}%")
    else:
        fraud_col = None
        fraud_count = 0
        fraud_pct = 0
        print("No fraud labels found.")

    # Risk scoring: flag high-amount outliers
    amount_col = 'Amount' if 'Amount' in df.columns else None
    if amount_col:
        q99 = df[amount_col].quantile(0.99)
        q95 = df[amount_col].quantile(0.95)
        df['risk_flag'] = df[amount_col].apply(
            lambda x: 'CRITICAL' if x > q99 else 'HIGH' if x > q95 else 'NORMAL'
        )
        high_risk = len(df[df['risk_flag'].isin(['CRITICAL', 'HIGH'])])
        print(f"High-risk transactions (amount): {high_risk}")
    else:
        df['risk_flag'] = 'UNKNOWN'
        high_risk = 0

    # Generate charts
    charts = generate_charts(df, fraud_col, amount_col)

    # Build HTML
    report_file = build_html(df, fraud_col, amount_col, charts, fraud_count, fraud_pct, high_risk)
    print(f"\n✅ Dashboard generated: {report_file}")

    # Export flagged
    flagged = df[df['risk_flag'].isin(['CRITICAL', 'HIGH'])] if 'risk_flag' in df.columns else df.head(0)
    if not flagged.empty:
        flagged.to_csv('flagged_transactions.csv', index=False)
        print(f"✅ Flagged transactions exported: {len(flagged)} records")

    return df

def fig_to_base64(fig):
    buf = BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode("utf-8")
    plt.close(fig)
    return b64

def generate_charts(df, fraud_col, amount_col):
    charts = {}

    # Chart 1: Fraud vs Normal distribution (if Class exists)
    if fraud_col:
        fig, ax = plt.subplots()
        counts = df[fraud_col].value_counts().sort_index()
        labels = ['Normal', 'Fraud']
        colors = ['#43a047', '#e53935']
        ax.bar(labels, [counts.get(0, 0), counts.get(1, 0)], color=colors)
        ax.set_title('Transaction Distribution')
        ax.set_ylabel('Count')
        charts['fraud_dist'] = fig_to_base64(fig)

    # Chart 2: Amount distribution (log scale)
    if amount_col:
        fig, ax = plt.subplots()
        normal = df[df[fraud_col] == 0][amount_col] if fraud_col else df[amount_col]
        fraud = df[df[fraud_col] == 1][amount_col] if fraud_col else pd.Series()

        ax.hist(normal, bins=50, alpha=0.7, label='Normal', color='#43a047', density=True)
        if not fraud.empty:
            ax.hist(fraud, bins=50, alpha=0.7, label='Fraud', color='#e53935', density=True)
        ax.set_xlabel('Transaction Amount')
        ax.set_ylabel('Density')
        ax.set_title('Amount Distribution: Normal vs Fraud')
        ax.legend()
        charts['amount_dist'] = fig_to_base64(fig)

    # Chart 3: Risk flag breakdown
    if 'risk_flag' in df.columns:
        fig, ax = plt.subplots()
        risk_counts = df['risk_flag'].value_counts()
        colors_map = {'NORMAL': '#43a047', 'HIGH': '#fb8c00', 'CRITICAL': '#e53935', 'UNKNOWN': '#9e9e9e'}
        bar_colors = [colors_map.get(x, 'gray') for x in risk_counts.index]
        risk_counts.plot(kind='barh', ax=ax, color=bar_colors)
        ax.set_title('Risk Flag Breakdown')
        ax.set_xlabel('Count')
        charts['risk_flags'] = fig_to_base64(fig)

    # Chart 4: Top 10 highest amounts
    if amount_col:
        fig, ax = plt.subplots()
        top10 = df.nlargest(10, amount_col)
        colors_top = ['#e53935' if (fraud_col and row[fraud_col] == 1) else '#3949ab' for _, row in top10.iterrows()]
        ax.barh(range(10), top10[amount_col].values, color=colors_top)
        ax.set_yticks(range(10))
        ax.set_yticklabels([f"TXN-{i}" for i in top10.index])
        ax.set_xlabel('Amount ($)')
        ax.set_title('Top 10 Highest Transactions (Red = Fraud)')
        charts['top10'] = fig_to_base64(fig)

    return charts

def build_html(df, fraud_col, amount_col, charts, fraud_count, fraud_pct, high_risk):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = f"Fintech_Dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

    # Summary stats
    total = len(df)
    avg_amount = df[amount_col].mean() if amount_col else 0
    max_amount = df[amount_col].max() if amount_col else 0

    # Top suspicious transactions
    if amount_col:
        suspicious = df.nlargest(5, amount_col)
        cols = ['Amount'] + ([fraud_col] if fraud_col else [])
        suspicious_html = suspicious[cols].to_html(classes='table table-critical', index=False)
    else:
        suspicious_html = "<p>No amount data available.</p>"

    chart_html = ""
    for name, b64 in charts.items():
        chart_html += f'<h3>{name.replace("_", " ").title()}</h3><img src="data:image/png;base64,{b64}" style="max-width:100%;height:auto;"><br><br>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Fintech Fraud Detection Dashboard</title>
<style>
body{{font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;max-width:1000px;margin:40px auto;padding:20px;background:#f5f7fa;color:#333}}
.container{{background:#fff;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
h1{{color:#1a237e;border-bottom:3px solid #3949ab;padding-bottom:10px}}
h2{{color:#3949ab;margin-top:25px}}
h3{{color:#555;margin-top:18px;font-size:1em}}
.stat-box{{display:inline-block;background:#e8eaf6;padding:15px 25px;margin:8px;border-radius:6px;text-align:center;min-width:120px}}
.stat-box strong{{display:block;font-size:1.6em;color:#1a237e}}
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
<h1>🔥 Fintech Fraud Detection Dashboard</h1>
<p style="color:#777">Generated: {timestamp}</p>

<div>
  <div class="stat-box"><strong>{total:,}</strong>Total Transactions</div>
  <div class="stat-box"><strong>{fraud_count}</strong>Fraud Cases</div>
  <div class="stat-box"><strong>{fraud_pct:.4f}%</strong>Fraud Rate</div>
  <div class="stat-box"><strong>{high_risk}</strong>High-Risk Amounts</div>
  <div class="stat-box"><strong>${avg_amount:.2f}</strong>Avg Amount</div>
  <div class="stat-box"><strong>${max_amount:.2f}</strong>Max Amount</div>
</div>

<h2>🚨 Top Suspicious Transactions</h2>
{suspicious_html}

<h2>📊 Visualizations</h2>
{chart_html}

<div class="footer">
Fintech Fraud Detector v2 | Automated by SPAA<br>
Python + Pandas + Matplotlib | Real-Time Risk Scoring Pipeline
</div>
</div>
</body>
</html>"""

    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

if __name__ == "__main__":
    CSV_FILE = "creditcard.csv"

    import os
    if not os.path.exists(CSV_FILE):
        print(f"⚠️  File not found: {CSV_FILE}")
        print("Please download the Kaggle Credit Card Fraud dataset and place it in this folder.")
    else:
        analyze_fraud(CSV_FILE)