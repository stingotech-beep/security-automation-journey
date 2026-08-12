import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_logs(n=1000):
    roles = ['Doctor', 'Nurse', 'Admin', 'Billing']
    depts = ['Cardiology', 'Oncology', 'Emergency', 'Pediatrics', 'Radiology']
    actions = ['VIEW', 'EDIT', 'PRINT', 'EXPORT']
    
    data = []
    base_time = datetime(2026, 8, 1, 8, 0)
    
    for i in range(n):
        # Normal hours: 8AM-6PM weighted higher
        hour = random.choices(
            range(24), 
            weights=[2,1,1,1,1,1,2,3, 5,5,5,5,5,5,5,5,5,5,4,3,2,2,2,2]
        )[0]
        
        timestamp = base_time + timedelta(days=random.randint(0,30), hours=hour)
        user_id = f"USER_{random.randint(100,199)}"
        role = random.choice(roles)
        dept = random.choice(depts)
        patient_id = f"PAT_{random.randint(1000,9999)}"
        action = random.choice(actions)
        
        data.append([timestamp, user_id, role, dept, patient_id, action])
    
    df = pd.DataFrame(data, columns=['timestamp','user_id','role','department','patient_id','action'])
    
    # Inject anomalies
    # 1. After-hours access (2AM-4AM)
    for _ in range(15):
        idx = random.randint(0, n-1)
        new_time = df.loc[idx, 'timestamp'].replace(hour=random.choice([2,3,4,23]))
        df.loc[idx, 'timestamp'] = new_time
    
    # 2. Cross-department violation (Billing viewing clinical records)
    for _ in range(10):
        idx = random.randint(0, n-1)
        df.loc[idx, 'role'] = 'Admin'
        df.loc[idx, 'department'] = 'Billing'
    
    df.to_csv('healthcare_access_logs.csv', index=False)
    print(f"✅ Generated healthcare_access_logs.csv with {n} records")

if __name__ == "__main__":
    generate_logs()