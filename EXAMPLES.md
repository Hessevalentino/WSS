# WiFi Scanner Suite - Usage Examples

This document provides practical examples of using WiFi Scanner Suite (WSS) for various network analysis scenarios.

## Basic Usage Examples

### Quick Network Scan
Perform a one-time scan to discover available networks:
```bash
python3 wifi_scanner_suite.py --scan
```

### Automated Open Network Testing
Test all open networks and generate a comprehensive report:
```bash
python3 wifi_scanner_suite.py --auto
```

### Continuous Monitoring
Monitor WiFi networks in real-time with live updates:
```bash
python3 wifi_scanner_suite.py --continuous
```

## Interactive Menu Examples

### Starting Interactive Mode
```bash
python3 wifi_scanner_suite.py
```

The interactive menu provides these options:
1. **Continuous scanning** - Real-time network monitoring
2. **Auto-connect** - Test all open networks systematically
3. **Show statistics** - View scan results and connection data
4. **Export data** - Save results in JSON or CSV format
5. **Settings** - Display current configuration
6. **Show logs** - Browse historical data

## Configuration Examples

### Custom Configuration File
Create `wifi_config.json` with custom settings:
```json
{
  "interface": "wlp3s0",
  "test_host": "1.1.1.1",
  "scan_interval": 5,
  "log_dir": "/home/user/wifi_logs",
  "ping_timeout": 3,
  "connection_timeout": 10
}
```

### Different Network Interfaces
For systems with multiple wireless interfaces:
```json
{
  "interface": "wlan1"
}
```

### Alternative Connectivity Test Hosts
```json
{
  "test_host": "1.1.1.1"
}
```

## Output Examples

### Successful Connection Report
```
CONNECTION REPORT
============================================================

Summary:
  • Total networks tested: 5
  • Successful connections: 2
  • Failed connections: 3

WORKING NETWORKS (2):
  CafeWiFi
     IP: 192.168.1.105 | Signal: 78% | Band: 2.4GHz | Ping: min/avg/max = 15.2/18.7/22.1 ms
  
  LibraryFree
     IP: 10.0.0.50 | Signal: 65% | Band: 5GHz | Ping: min/avg/max = 8.9/12.3/16.7 ms

NON-WORKING NETWORKS (3):
  FreeHotspot
     Reason: Failed to get IP address | Signal: 45% | Band: 2.4GHz
  
  PublicAccess
     Reason: Connection failed | Signal: 38% | Band: 2.4GHz
  
  OpenNet
     Reason: Connection timeout | Signal: 52% | Band: 5GHz
============================================================
```

### Continuous Scan Output
```
WiFi Scan #3 - 15:42:18
┌─────────────────┬──────────────┬────────────┬─────────┬─────────────┐
│ SSID            │ Security     │ Signal     │ Band    │ Quality     │
├─────────────────┼──────────────┼────────────┼─────────┼─────────────┤
│ HomeNetwork     │ WPA2         │ 89% (-42dBm)│ 5GHz    │ Excellent   │
│ CafeWiFi        │ OPEN         │ 76% (-48dBm)│ 2.4GHz  │ Good        │
│ NeighborWiFi    │ WPA2         │ 62% (-55dBm)│ 2.4GHz  │ Good        │
│ PublicHotspot   │ OPEN         │ 41% (-68dBm)│ 2.4GHz  │ Weak        │
└─────────────────┴──────────────┴────────────┴─────────┴─────────────┘

Statistics:
  • Total networks: 4
  • Open: 2
  • 2.4GHz: 3
  • 5GHz: 1
```

## Export Examples

### JSON Export
```bash
# Export current session data
python3 wifi_scanner_suite.py
# Select option 4 (Export data)
# Choose JSON format
```

Sample JSON output:
```json
{
  "timestamp": "2024-01-15T15:42:18.123456",
  "networks": [
    {
      "ssid": "CafeWiFi",
      "security": "",
      "signal": 76,
      "frequency": 2437,
      "band": "2.4GHz",
      "channel": 6,
      "bssid": "aa:bb:cc:dd:ee:ff",
      "rssi": -48,
      "timestamp": "2024-01-15T15:42:18.123456"
    }
  ],
  "connection_attempts": [
    {
      "ssid": "CafeWiFi",
      "timestamp": "2024-01-15T15:42:25.123456",
      "success": true,
      "ip_address": "192.168.1.105",
      "band": "2.4GHz",
      "signal": 76,
      "ping_success": true,
      "ping_stats": "min/avg/max = 15.2/18.7/22.1 ms"
    }
  ]
}
```

### CSV Export
CSV files are generated separately for networks and connection attempts:

**wifi_networks_20240115_154218.csv**
```csv
ssid,security,signal,frequency,band,channel,bssid,rssi,timestamp
CafeWiFi,,76,2437,2.4GHz,6,aa:bb:cc:dd:ee:ff,-48,2024-01-15T15:42:18.123456
PublicHotspot,,41,2462,2.4GHz,11,bb:cc:dd:ee:ff:aa,-68,2024-01-15T15:42:18.123456
```

**wifi_attempts_20240115_154218.csv**
```csv
ssid,timestamp,success,ip_address,error_message,band,signal,ping_success,ping_stats
CafeWiFi,2024-01-15T15:42:25.123456,True,192.168.1.105,,2.4GHz,76,True,min/avg/max = 15.2/18.7/22.1 ms
PublicHotspot,2024-01-15T15:42:35.123456,False,,Failed to get IP address,2.4GHz,41,False,
```

## Troubleshooting Examples

### Permission Issues
```bash
# If you encounter permission errors:
sudo python3 wifi_scanner_suite.py

# Or add user to netdev group:
sudo usermod -a -G netdev $USER
# Then logout and login again
```

### Interface Detection
```bash
# List available wireless interfaces:
ip link show | grep wl

# Check interface status:
iwconfig

# Verify NetworkManager is managing the interface:
nmcli device status
```

### Network Manager Conflicts
```bash
# Stop conflicting services:
sudo systemctl stop wpa_supplicant
sudo systemctl stop dhcpcd

# Ensure NetworkManager is running:
sudo systemctl start NetworkManager
sudo systemctl enable NetworkManager
```

## Advanced Usage Scenarios

### Security Assessment
Use WSS to assess open network availability in different locations:
```bash
# Test in different locations and compare results
python3 wifi_scanner_suite.py --auto > location1_results.txt
# Move to different location
python3 wifi_scanner_suite.py --auto > location2_results.txt
```

### Network Coverage Analysis
Monitor signal strength changes over time:
```bash
# Run continuous scan and log results
python3 wifi_scanner_suite.py --continuous
# Results are automatically saved to wifi_logs directory
```

### Automated Reporting
Combine with system tools for automated reporting:
```bash
#!/bin/bash
# Daily WiFi survey script
DATE=$(date +%Y%m%d)
python3 wifi_scanner_suite.py --auto --no-banner > "wifi_survey_$DATE.txt"
```

## Integration Examples

### Cron Job Setup
Automate regular WiFi surveys:
```bash
# Edit crontab
crontab -e

# Add entry for daily scan at 2 AM
0 2 * * * /usr/bin/python3 /path/to/wifi_scanner_suite.py --scan --no-banner >> /var/log/wifi_daily.log 2>&1
```

### Log Analysis
Process exported JSON data with other tools:
```bash
# Extract open networks using jq
cat wifi_scan_20240115_154218.json | jq '.networks[] | select(.security == "") | .ssid'

# Count networks by band
cat wifi_scan_20240115_154218.json | jq '.networks | group_by(.band) | map({band: .[0].band, count: length})'
```

This examples file demonstrates the versatility and practical applications of WiFi Scanner Suite for various network analysis and monitoring tasks.
