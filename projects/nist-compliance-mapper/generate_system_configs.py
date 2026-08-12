import pandas as pd
import random

def generate_configs(n=200):
    controls = {
        'AC-2': 'Account Management',
        'AU-6': 'Audit Review',
        'CM-2': 'Baseline Configuration',
        'IA-2': 'Identification & Authentication',
        'SC-7': 'Boundary Protection',
        'SI-4': 'Information System Monitoring'
    }
    
    data = []
    for i in range(n):
        control_id = random.choice(list(controls.keys()))
        status = random.choices(['Pass', 'Fail', 'Partial'], weights=[60, 25, 15])[0]
        severity = 'Critical' if control_id in ['SC-7', 'IA-2'] and status == 'Fail' else 'Medium'
        
        data.append([
            f"SERVER-{100+i}", control_id, controls[control_id],
            status, severity, random.randint(1, 100)
        ])
    
    df = pd.DataFrame(data, columns=['hostname','control_id','control_name','status','severity','score'])
    df.to_csv('system_configs.csv', index=False)
    print(f"✅ Generated system_configs.csv with {n} records")

if __name__ == "__main__":
    generate_configs()