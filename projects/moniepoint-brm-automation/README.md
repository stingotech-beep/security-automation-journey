#!/usr/bin/env python3
"""
Moniepoint BRM Performance Automation
SPAA Project: Security + Python + Analytics + Automation

Automates message generation for business owners based on daily performance.
"""

import pandas as pd
import os
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIGURATION - Edit these for your needs
# ---------------------------------------------------------------------------
REPORT_FILE = "daily_performance_report.csv"  # Your daily report
OUTPUT_FOLDER = "brm_output"
TODAY = datetime.now().strftime("%Y-%m-%d")

# Target thresholds (customize these)
DAILY_TARGET = 50000  # ₦50,000 daily transaction target
LOAN_MIN_TRANSACTIONS = 100
LOAN_MIN_VOLUME = 2000000  # ₦2M monthly volume

# ---------------------------------------------------------------------------
# MESSAGE TEMPLATES
# ---------------------------------------------------------------------------
MESSAGES = {
    "meeting_target": """Dear {name},

Great job! 🎉 Your business hit ₦{performance:,} today — you're on track and exceeding expectations.

Keep the momentum going. Your consistency unlocks higher limits and premium support.

Best,
{brm_name}
Moniepoint Business Banking""",

    "non_meeting": """Dear {name},

We noticed your transactions today were ₦{performance:,}, below your ₦{target:,} daily target.

Let's fix this together. Reply with your biggest challenge this week — terminal issues? Low foot traffic? I'm here to help.

Best,
{brm_name}
Moniepoint Business Banking""",

    "loan_qualified": """Dear {name},

Congratulations! 🎊 Based on your strong transaction history (₦{performance:,} avg daily), you pre-qualify for a Moniepoint business loan.

Amount: Up to ₦{loan_amount:,}
Interest: From 3% monthly
Disbursement: 24 hours

Reply LOAN to schedule a 5-minute call.

Best,
{brm_name}
Moniepoint Business Banking""",

    "new_onboarding": """Dear {name},

Welcome to Moniepoint! 🎉 Your terminal is active and ready.

Your first-week target: ₦{target:,} in transactions.
Need help? Call me directly or reply HELP.

Let's grow your business together.

Best,
{brm_name}
Moniepoint Business Banking"""
}

# ---------------------------------------------------------------------------
# CORE ENGINE
# ---------------------------------------------------------------------------
def categorize_merchants(df):
    """Categorize each merchant based on performance."""
    categories = []
    
    for _, row in df.iterrows():
        performance = row.get('daily_volume', 0)
        tenure_days = row.get('tenure_days', 0)
        total_transactions = row.get('total_transactions', 0)
        
        # Logic
        if tenure_days <= 7:
            cat = "new_onboarding"
        elif performance >= DAILY_TARGET * 1.2 and total_transactions >= LOAN_MIN_TRANSACTIONS:
            cat = "loan_qualified"
        elif performance >= DAILY_TARGET:
            cat = "meeting_target"
        else:
            cat = "non_meeting"
        
        categories.append(cat)
    
    df['category'] = categories
    return df

def generate_messages(df, brm_name="Your BRM"):
    """Generate personalized messages for each merchant."""
    messages = []
    
    for _, row in df.iterrows():
        cat = row['category']
        template = MESSAGES.get(cat, MESSAGES['non_meeting'])
        
        # Calculate loan amount (example: 20% of monthly volume)
        loan_amount = int(row.get('monthly_volume', 0) * 0.2) if cat == 'loan_qualified' else 0
        
        message = template.format(
            name=row.get('business_name', 'Valued Partner'),
            performance=int(row.get('daily_volume', 0)),
            target=DAILY_TARGET,
            loan_amount=loan_amount,
            brm_name=brm_name
        )
        
        messages.append(message)
    
    df['message'] = messages
    return df

def export_by_category(df):
    """Export separate files for each category."""
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    summary = {}
    
    for category in df['category'].unique():
        subset = df[df['category'] == category].copy()
        filename = f"{OUTPUT_FOLDER}/{category}_{TODAY}.csv"
        subset.to_csv(filename, index=False)
        
        # Also export phone + message for WhatsApp bulk
        if 'phone' in subset.columns:
            whatsapp_file = f"{OUTPUT_FOLDER}/{category}_whatsapp_{TODAY}.txt"
            with open(whatsapp_file, 'w', encoding='utf-8') as f:
                for _, row in subset.iterrows():
                    f.write(f"{row['phone']}\n{row['message']}\n\n---\n\n")
        
        summary[category] = len(subset)
        print(f"✅ Exported {len(subset)} records to {filename}")
    
    return summary

def generate_dashboard(df, summary):
    """Generate HTML dashboard for managers."""
    total = len(df)
    meeting = summary.get('meeting_target', 0)
    non_meeting = summary.get('non_meeting', 0)
    loan = summary.get('loan_qualified', 0)
    new_merchants = summary.get('new_onboarding', 0)
    
    # Performance stats
    avg_volume = df['daily_volume'].mean() if 'daily_volume' in df.columns else 0
    top_performer = df.loc[df['daily_volume'].idxmax()] if 'daily_volume' in df.columns else None
    
    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Moniepoint BRM Dashboard - {TODAY}</title>
<style>
body{{font-family:Segoe UI,sans-serif;max-width:900px;margin:40px auto;padding:20px;background:#f5f7fa}}
.container{{background:#fff;padding:30px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.1)}}
h1{{color:#1a237e;border-bottom:3px solid #3949ab;padding-bottom:10px}}
.stat-box{{display:inline-block;padding:15px 25px;margin:8px;border-radius:6px;text-align:center;min-width:120px;color:#fff}}
.meeting{{background:#43a047}}
.non-meeting{{background:#e53935}}
.loan{{background:#fb8c00}}
.new{{background:#3949ab}}
.total{{background:#1a237e}}
table{{border-collapse:collapse;width:100%;margin-top:15px;font-size:0.9em}}
th,td{{border:1px solid #ddd;padding:8px;text-align:left}}
th{{background:#3949ab;color:#fff}}
tr:nth-child(even){{background:#f9f9f9}}
.footer{{margin-top:30px;color:#999;font-size:0.85em;text-align:center;border-top:1px solid #ddd;padding-top:14px}}
</style>
</head>
<body>
<div class="container">
<h1>📊 Moniepoint BRM Performance Dashboard</h1>
<p style="color:#777">Date: {TODAY} | Generated by SPAA Automation</p>

<div>
  <div class="stat-box total"><strong>{total}</strong><br>Total Merchants</div>
  <div class="stat-box meeting"><strong>{meeting}</strong><br>Meeting Target</div>
  <div class="stat-box non-meeting"><strong>{non_meeting}</strong><br>Below Target</div>
  <div class="stat-box loan"><strong>{loan}</strong><br>Loan Qualified</div>
  <div class="stat-box new"><strong>{new_merchants}</strong><br>New This Week</div>
</div>

<h2>💰 Performance Summary</h2>
<p><strong>Average Daily Volume:</strong> ₦{avg_volume:,.0f}</p>
<p><strong>Daily Target:</strong> ₦{DAILY_TARGET:,.0f}</p>

<h2>🏆 Top Performer</h2>
<p>{f"<strong>{top_performer['business_name']}</strong> — ₦{top_performer['daily_volume']:,.0f}" if top_performer is not None else "No data available"}</p>

<h2>📱 Message Export Status</h2>
<table>
<tr><th>Category</th><th>Count</th><th>Status</th></tr>
<tr><td>Meeting Target</td><td>{meeting}</td><td>✅ Ready</td></tr>
<tr><td>Non-Meeting</td><td>{non_meeting}</td><td>✅ Ready</td></tr>
<tr><td>Loan Qualified</td><td>{loan}</td><td>✅ Ready</td></tr>
<tr><td>New Onboarding</td><td>{new_merchants}</td><td>✅ Ready</td></tr>
</table>

<div class="footer">
Moniepoint BRM Automation | Built with SPAA<br>
Python + Pandas | Daily Performance Pipeline
</div>
</div>
</body>
</html>"""
    
    filename = f"{OUTPUT_FOLDER}/brm_dashboard_{TODAY}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"\n✅ Dashboard generated: {filename}")
    return filename

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print("=" * 50)
    print("MONIEPOINT BRM AUTOMATION SYSTEM")
    print("=" * 50)
    
    # Check for report file
    if not os.path.exists(REPORT_FILE):
        print(f"\n⚠️  Report file not found: {REPORT_FILE}")
        print("\nCreating sample data for demonstration...")
        create_sample_data()
    
    # Load data
    print(f"\n📥 Loading: {REPORT_FILE}")
    df = pd.read_csv(REPORT_FILE)
    print(f"Loaded {len(df)} merchant records")
    
    # Process
    print("\n🧠 Categorizing merchants...")
    df = categorize_merchants(df)
    
    print("\n✉️  Generating personalized messages...")
    df = generate_messages(df, brm_name="Your Name")
    
    # Export
    print("\n📤 Exporting by category...")
    summary = export_by_category(df)
    
    # Dashboard
    print("\n📊 Generating manager dashboard...")
    dashboard_file = generate_dashboard(df, summary)
    
    print("\n" + "=" * 50)
    print("AUTOMATION COMPLETE")
    print("=" * 50)
    print(f"\nCheck the '{OUTPUT_FOLDER}/' folder for:")
    print("  - CSV files per category")
    print("  - WhatsApp-ready message files")
    print("  - HTML dashboard for managers")

def create_sample_data():
    """Create sample data for demonstration."""
    import random
    
    data = []
    names = ["Ade Stores", "Chukwu Ventures", "Fatima Boutique", "Ibrahim Electronics",
             "Ngozi Provisions", "Oluwaseun Mart", "Amina Traders", "Emeka Hardware",
             "Yusuf Comm.", "Blessing Salon", "Tunde Pharma", "Zainab Fashions"]
    
    for i, name in enumerate(names):
        data.append({
            'business_name': name,
            'phone': f"080{random.randint(10000000, 99999999)}",
            'daily_volume': random.randint(15000, 120000),
            'monthly_volume': random.randint(500000, 5000000),
            'total_transactions': random.randint(20, 300),
            'tenure_days': random.randint(2, 180)
        })
    
    sample_df = pd.DataFrame(data)
    sample_df.to_csv(REPORT_FILE, index=False)
    print(f"✅ Sample data created: {REPORT_FILE}")

if __name__ == "__main__":
    main()
