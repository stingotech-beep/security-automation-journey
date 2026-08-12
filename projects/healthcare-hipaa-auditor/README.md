# Healthcare HIPAA Access Auditor

Automated compliance auditing for healthcare access logs.

## Dataset
- Simulated hospital access logs (1000 events)
- Columns: timestamp, user_id, role, department, patient_id, action

## Violations Detected
- After-hours access (before 6 AM / after 10 PM)
- Cross-department access (Billing staff viewing clinical records)
- Bulk access (&gt;15 records by one user per day)

## SPAA Pillars
- **Security:** HIPAA compliance, unauthorized access detection
- **Python:** Log parsing, datetime manipulation
- **Analytics:** Pattern detection, anomaly flagging
- **Automation:** One-command audit + CSV export
