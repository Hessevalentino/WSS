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

### Continuous Monitoring with BSSID Display
Monitor WiFi networks in real-time with live updates including BSSID information:
```bash
python3 wifi_scanner_suite.py --continuous
```

**Sample output with BSSID:**
```
WiFi Scan #1 - 17:30:45
┌─────────────────┬──────────┬────────┬─────────┬───────────────────┬─────────────┐
│ SSID            │ Security │ Signal │ Band    │ BSSID             │ Quality     │
├─────────────────┼──────────┼────────┼─────────┼───────────────────┼─────────────┤
│ HomeNetwork     │ 🔒 WPA2  │ 85%    │ 2.4GHz  │ AA:BB:CC:DD:EE:FF │ Excellent   │
│ FreeWiFi        │ 🔓 OPEN  │ 72%    │ 5GHz    │ BB:CC:DD:EE:FF:AA │ Good        │
│ CoffeeShop      │ 🔓 OPEN  │ 45%    │ 2.4GHz  │ CC:DD:EE:FF:AA:BB │ Weak        │
└─────────────────┴──────────┴────────┴─────────┴───────────────────┴─────────────┘

🎉 OPEN NETWORKS FOUND:
  → FreeWiFi (72% -58dBm 5GHz) | BSSID: BB:CC:DD:EE:FF:AA [OPEN]
  → CoffeeShop (45% -76dBm 2.4GHz) | BSSID: CC:DD:EE:FF:AA:BB [OPEN]
```

## Interactive Menu Examples

### Starting Interactive Mode
```bash
python3 wifi_scanner_suite.py
```

The interactive menu provides these options:
1. **Continuous scanning** - Real-time network monitoring
2. **Auto-connect** - Test all open networks systematically
3. **Scan network devices** - Discover devices connected to current network
4. **Show statistics** - View scan results and connection data
5. **Export to JSON** - Save results with network and device information
6. **Settings** - Display current configuration
7. **Log viewer** - Browse historical data including device information

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

## Network Device Discovery Examples

### Basic Device Scanning
Use menu option 3 to discover devices on the current network:
```
🖥️  Scanning network devices...

✅ Found 6 network devices
┌─────────────────┬───────────────────┬──────────────────┬─────────────────────┐
│ IP Address      │ MAC Address       │ Hostname         │ Vendor              │
├─────────────────┼───────────────────┼──────────────────┼─────────────────────┤
│ 192.168.1.1     │ AA:BB:CC:DD:EE:FF │ router.local     │ Cisco Systems       │
│ 192.168.1.100   │ BB:CC:DD:EE:FF:AA │ laptop           │ Dell Inc.           │
│ 192.168.1.50    │ CC:DD:EE:FF:AA:BB │ -                │ Apple Inc.          │
│ 192.168.1.25    │ DD:EE:FF:AA:BB:CC │ smartphone       │ Samsung Electronics │
│ 192.168.1.75    │ EE:FF:AA:BB:CC:DD │ tablet           │ Apple Inc.          │
│ 192.168.1.200   │ FF:AA:BB:CC:DD:EE │ printer          │ HP Inc.             │
└─────────────────┴───────────────────┴──────────────────┴─────────────────────┘
```

### Device Discovery Methods
WSS uses multiple scanning methods for comprehensive device discovery:

1. **ARP Table Scanning** (fastest)
   - Scans existing ARP entries
   - Discovers recently communicated devices
   - Provides hostname information

2. **Active Network Scanning** (most comprehensive)
   - Uses `arp-scan` for complete network mapping
   - Discovers all active devices on subnet
   - Provides vendor identification

3. **Nmap Fallback** (when arp-scan unavailable)
   - Uses `nmap -sn` for ping sweep
   - Discovers responsive devices
   - Extracts MAC addresses and vendors

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

### JSON Export with Device Information
```bash
# Export current session data including network devices
python3 wifi_scanner_suite.py
# Select option 5 (Export to JSON)
```

Sample JSON output with network devices:
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
  ],
  "network_devices": [
    {
      "ip_address": "192.168.1.1",
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "hostname": "router.local",
      "vendor": "Cisco Systems",
      "timestamp": "2024-01-15T15:42:18.123456"
    },
    {
      "ip_address": "192.168.1.100",
      "mac_address": "BB:CC:DD:EE:FF:AA",
      "hostname": "laptop",
      "vendor": "Dell Inc.",
      "timestamp": "2024-01-15T15:42:18.123456"
    },
    {
      "ip_address": "192.168.1.50",
      "mac_address": "CC:DD:EE:FF:AA:BB",
      "hostname": null,
      "vendor": "Apple Inc.",
      "timestamp": "2024-01-15T15:42:18.123456"
    }
  ]
}
```

## Log Viewer Examples

### Browsing Historical Data
Use menu option 7 to browse historical scan data:
```
📋 LOG VIEWER
============================================================

Available log files:
┌───┬─────────────────────────────┬─────────┬──────────────────┬──────────┬─────────────┐
│ # │ File Name                   │ Size    │ Date             │ Networks │ Attempts    │
├───┼─────────────────────────────┼─────────┼──────────────────┼──────────┼─────────────┤
│ 1 │ wifi_scan_20240115_154218   │ 2.3KB   │ 15.01.2024 15:42 │ 5        │ 3           │
│ 2 │ wifi_scan_20240115_143022   │ 1.8KB   │ 15.01.2024 14:30 │ 3        │ 2           │
│ 3 │ wifi_scan_20240114_162545   │ 3.1KB   │ 14.01.2024 16:25 │ 8        │ 5           │
└───┴─────────────────────────────┴─────────┴──────────────────┴──────────┴─────────────┘
```

### Viewing Networks with BSSID in Logs
After selecting a log file, option 1 shows all networks including BSSID information:
```
📄 LOG: wifi_scan_20240115_154218.json
Timestamp: 2024-01-15T15:42:18.123456
Networks found: 5
Connection attempts: 3
Network devices: 6

Options:
1. View all networks      ← Shows BSSID information
2. View open networks only
3. View connection attempts
4. View network devices
5. View statistics
6. Back to log list
```

**Network display with BSSID:**
```
All Networks (5)
┌─────────────────┬──────────┬────────┬─────────┬───────────────────┬─────────┬──────────┐
│ SSID            │ Security │ Signal │ Band    │ BSSID             │ Channel │ RSSI     │
├─────────────────┼──────────┼────────┼─────────┼───────────────────┼─────────┼──────────┤
│ HomeNetwork     │ WPA2     │ 85%    │ 2.4GHz  │ AA:BB:CC:DD:EE:FF │ 6       │ -45dBm   │
│ FreeWiFi        │ OPEN     │ 72%    │ 5GHz    │ BB:CC:DD:EE:FF:AA │ 36      │ -58dBm   │
│ CoffeeShop      │ OPEN     │ 45%    │ 2.4GHz  │ CC:DD:EE:FF:AA:BB │ 11      │ -76dBm   │
└─────────────────┴──────────┴────────┴─────────┴───────────────────┴─────────┴──────────┘
```

### Viewing Device Information in Logs
Option 4 shows discovered network devices:

### Device Information Display
```
🖥️  Network Devices (6)
┌─────────────────┬───────────────────┬──────────────────┬─────────────────────┬───────────┐
│ IP Address      │ MAC Address       │ Hostname         │ Vendor              │ Timestamp │
├─────────────────┼───────────────────┼──────────────────┼─────────────────────┼───────────┤
│ 192.168.1.1     │ AA:BB:CC:DD:EE:FF │ router.local     │ Cisco Systems       │ 15:42:18  │
│ 192.168.1.100   │ BB:CC:DD:EE:FF:AA │ laptop           │ Dell Inc.           │ 15:42:18  │
│ 192.168.1.50    │ CC:DD:EE:FF:AA:BB │ -                │ Apple Inc.          │ 15:42:18  │
│ 192.168.1.25    │ DD:EE:FF:AA:BB:CC │ smartphone       │ Samsung Electronics │ 15:42:18  │
│ 192.168.1.75    │ EE:FF:AA:BB:CC:DD │ tablet           │ Apple Inc.          │ 15:42:18  │
│ 192.168.1.200   │ FF:AA:BB:CC:DD:EE │ printer          │ HP Inc.             │ 15:42:18  │
└─────────────────┴───────────────────┴──────────────────┴─────────────────────┴───────────┘
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
