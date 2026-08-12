#!/usr/bin/env python3
"""
NIST 800-53 Compliance Mapper v1
SPAA Project: Security + Python + Analytics + Automation
"""

import pandas as pd

def map_compliance(csv_path: str):
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"\nTotal controls checked: {len(df)}")
    print(f"Unique systems: {df['hostname'].nunique()}")
    
    # Summary by status
    print(f"\n{'='*50}")
    print("COMPLIANCE SUMMARY")
    print(f"{'='*50}")
    print(df['status'].value_counts())
    
    # Critical failures
    critical = df[(df['status'] == 'Fail') & (df['severity'] == 'Critical')]
    print(f"\n🚨 CRITICAL FAILURES: {len(critical)}")
    if len(critical) > 0:
        print(critical[['hostname','control_id','control_name','score']].to_string(index=False))
    
    # Compliance score
    pass_count = len(df[df['status'] == 'Pass'])
    compliance_pct = (pass_count / len(df)) * 100
    
    print(f"\n{'='*50}")
    print(f"OVERALL COMPLIANCE: {compliance_pct:.1f}%")
    print(f"{'='*50}")
    print(f"Pass: {pass_count} | Fail: {len(df[df['status']=='Fail'])} | Partial: {len(df[df['status']=='Partial'])}")
    
    # Export audit report
    df.to_csv('nist_audit_report.csv', index=False)
    print(f"\n✅ Exported to nist_audit_report.csv")
    
    return df

if __name__ == "__main__":
    import os
    if not os.path.exists('system_configs.csv'):
        import generate_system_configs
        generate_system_configs.generate_configs()
    
    map_compliance('system_configs.csv')