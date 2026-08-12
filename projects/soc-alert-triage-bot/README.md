# SOC Alert Triage Bot (Mini-SOAR)

An automated Security Operations Center (SOC) triage pipeline.

## Dataset
- Simulated SIEM alerts (1000 events)
- Types: Brute Force, Malware, DDoS, Phishing, Data Exfiltration

## Triage Logic
- **Auto-Close:** Low-confidence false positives (clean IPs, common ports)
- **Escalate:** Critical alerts (known bad IPs, multiple IOCs)
- **Enrich:** IP reputation scoring + alert correlation

## SPAA Pillars
- **Security:** SOC workflows, incident response, threat intel
- **Python:** JSON/CSV parsing, API simulation, automation logic
- **Analytics:** Risk scoring, alert clustering, trend detection
- **Automation:** One-command triage + auto-export
