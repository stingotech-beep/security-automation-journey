#!/usr/bin/env python3
"""
Fintech Fraud Detector v1
SPAA Project: Security + Python + Analytics + Automation

Loads transaction data and prints basic overview.
"""

import pandas as pd

def analyze_transactions(csv_path: str):
    """Load and inspect transaction data."""
    print(f"Loading: {csv_path}")
    df = pd.read_csv(csv_path)
    
    print(f"\nTotal transactions: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    print(f"\nFirst 5 rows:")
    print(df.head())
    
    print(f"\nBasic stats:")
    print(df.describe())
    
    # Check for fraud labels (if dataset has 'Class' column)
    if 'Class' in df.columns:
        fraud_count = df['Class'].sum()
        print(f"\nFraud cases detected: {fraud_count}")
        print(f"Fraud percentage: {(fraud_count/len(df)*100):.4f}%")
    
    return df

if __name__ == "__main__":
    # Update this path once you download the dataset
    CSV_FILE = "creditcard.csv"
    
    try:
        df = analyze_transactions(CSV_FILE)
        print("\n✅ v1 complete. Data loaded successfully.")
    except FileNotFoundError:
        print(f"\n⚠️  File not found: {CSV_FILE}")
        print("Download the Kaggle dataset and place it in this folder.")