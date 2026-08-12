# Supply Chain IoT Security Monitor

Automated monitoring of fleet IoT devices for security anomalies.

## Dataset
- Simulated IoT fleet: 500 devices (GPS trackers, temp sensors, scanners)
- Fields: device_id, type, location, status, last_seen, open_ports

## Anomalies Detected
- **Offline devices:** No heartbeat &gt; 24 hours
- **Impossible travel:** GPS jumps &gt; 500km in 1 hour
- **Open ports:** IoT devices with exposed services (SSH, Telnet, FTP)
- **After-hours activity:** Devices active outside business zones at night

## SPAA Pillars
- **Security:** IoT hardening, network scanning simulation, fleet protection
- **Python:** Device simulation, geolocation logic, port analysis
- **Analytics:** Outlier detection, time-series gaps, spatial analysis
- **Automation:** One-command fleet health report
