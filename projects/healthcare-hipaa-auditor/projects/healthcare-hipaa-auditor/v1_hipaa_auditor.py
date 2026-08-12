#!/usr/bin/env python3
"""
HIPAA Access Log Auditor v1
SPAA Project: Security + Python + Analytics + Automation

Detects unauthorized access patterns in healthcare logs.
"""

import pandas as pd
from datetime import datetime

def audit_hipaa_logs(csv_path: str):
    """Analyze access logs for HIPAA violations."""
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['hour'] = df['timestamp'].dt.hour
    df['date'] = df['timestamp'].dt.date
    
    print(f"\nTotal access events: {len(df)}")
    print(f"Unique users: {df['user_id'].nunique()}")
    print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # FLAG 1: After-hours access (before 6 AM or after 10 PM)
    after_hours = df[(df['hour'] < 6) | (df['hour'] >= 22)]
    print(f"\n🚨 AFTER-HOURS ACCESS: {len(after_hours)} events")
    print(after_hours[['timestamp','user_id','role','patient_id']].head())
    
    # FLAG 2: Cross-department violation (Billing viewing clinical records)
    cross_dept = df[(df['role'] == 'Admin') & 
                    (df['department'] == 'Billing') & 
                    (df['action'].isin(['VIEW','EDIT']))]
    print(f"\n🚨 CROSS-DEPT ACCESS (Billing Admin): {len(cross_dept)} events")
    
    # FLAG 3: Bulk access (>15 records by same user per day)
    daily_counts = df.groupby(['date', 'user_id']).size().reset_index(name='count')
    bulk = daily_counts[daily_counts['count'] > 15]
    print(f"\n🚨 BULK ACCESS VIOLATIONS: {len(bulk)} user-days")
    if len(bulk) > 0:
        print(bulk.head())
    
    # Combine all flags
    flagged_ids = set(after_hours.index).union(set(cross_dept.index))
    flagged = df.loc[list(flagged_ids)]
    
    print(f"\n{'='*50}")
    print(f"TOTAL FLAGGED EVENTS: {len(flagged)}")
    print(f"Flagged percentage: {(len(flagged)/len(df)*100):.2f}%")
    
    # Export violations
    flagged.to_csv('hipaa_violations.csv', index=False)
    print("\n✅ Exported to hipaa_violations.csv")
    
    return flagged

if __name__ == "__main__":
    CSV_FILE = 'healthcare_access_logs.csv'
    
    try:
        # Generate data if not found
        import os
        if not os.path.exists(CSV_FILE):
            print("Sample data not found. Generating...")
            import generate_sample_logs
            generate_sample_logs.generate_logs()
        
        audit_hipaa_logs(CSV_FILE)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
