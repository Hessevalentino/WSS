# WiFi Scanner Suite (WSS)

A comprehensive command-line WiFi network scanner and connection utility for Linux systems. WSS provides advanced WiFi network discovery, automated connection testing, and detailed reporting capabilities.

## Features

- **Continuous WiFi Scanning**: Real-time monitoring of available wireless networks
- **Automated Connection Testing**: Systematic testing of open networks with connectivity validation
- **Advanced Network Analysis**: Signal strength, frequency band detection, and RSSI measurements
- **Comprehensive Reporting**: Detailed connection reports with ping statistics and failure analysis
- **Multiple Export Formats**: JSON and CSV export capabilities for data analysis
- **Interactive Menu System**: User-friendly interface with rich terminal support
- **Logging and Statistics**: Persistent storage of scan results and connection attempts

## Requirements

### System Dependencies
- Linux operating system
- NetworkManager (`nmcli`)
- Wireless tools (`iwconfig`, `iwlist`)
- Python 3.7 or higher

### Python Dependencies
- `rich` (optional, for enhanced terminal interface)

## Installation

### Clone Repository
```bash
https://github.com/Hessevalentino/WSS.git
cd wifi-scanner-suite
```

### Install Python Dependencies
```bash
# Optional: Install rich for enhanced interface
pip install rich
```

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get install network-manager wireless-tools

# CentOS/RHEL/Fedora
sudo yum install NetworkManager wireless-tools
# or
sudo dnf install NetworkManager wireless-tools
```

## Usage

### Interactive Mode
```bash
python3 wifi_scanner_suite.py
```

### Command Line Options
```bash
# One-time network scan
python3 wifi_scanner_suite.py --scan

# Automated connection testing
python3 wifi_scanner_suite.py --auto

# Continuous monitoring
python3 wifi_scanner_suite.py --continuous

# Skip ASCII banner
python3 wifi_scanner_suite.py --no-banner

# Display help
python3 wifi_scanner_suite.py --help
```

## Menu Options

1. **Continuous Scanning**: Real-time WiFi network monitoring with live updates
2. **Auto-connect**: Automated testing of all open networks with comprehensive reporting
3. **Show Statistics**: Display scan results and connection attempt statistics
4. **Export Data**: Save results in JSON or CSV format
5. **Settings**: View current configuration parameters
6. **Show Logs**: Browse historical scan data

## Configuration

WSS uses a configuration file (`wifi_config.json`) with the following default settings:

```json
{
  "interface": "wlan0",
  "test_host": "8.8.8.8",
  "scan_interval": 10,
  "log_dir": "./wifi_logs",
  "max_log_age_days": 30,
  "ping_timeout": 5,
  "connection_timeout": 15,
  "auto_cleanup": true,
  "export_format": "json"
}
```

### Configuration Parameters

- `interface`: Wireless network interface name
- `test_host`: Host used for connectivity testing (default: Google DNS)
- `scan_interval`: Seconds between scans in continuous mode
- `log_dir`: Directory for storing log files
- `max_log_age_days`: Automatic log cleanup threshold
- `ping_timeout`: Timeout for ping tests in seconds
- `connection_timeout`: Timeout for connection attempts in seconds
- `auto_cleanup`: Enable automatic log cleanup
- `export_format`: Default export format (json/csv)

## Output Examples

### Network Scan Results
```
WiFi Scan #1 - 14:30:25
┌─────────────────┬──────────────┬────────┬─────────┬─────────────┐
│ SSID            │ Security     │ Signal │ Band    │ Quality     │
├─────────────────┼──────────────┼────────┼─────────┼─────────────┤
│ HomeNetwork     │ WPA2         │ 85%    │ 2.4GHz  │ Excellent   │
│ FreeWiFi        │ OPEN         │ 72%    │ 5GHz    │ Good        │
│ CoffeeShop      │ OPEN         │ 45%    │ 2.4GHz  │ Weak        │
└─────────────────┴──────────────┴────────┴─────────┴─────────────┘
```

### Connection Report
```
CONNECTION REPORT
============================================================

Summary:
  • Total networks tested: 3
  • Successful connections: 1
  • Failed connections: 2

WORKING NETWORKS (1):
  FreeWiFi
     IP: 192.168.1.100 | Signal: 72% | Band: 5GHz | Ping: min/avg/max = 12.3/15.6/18.9 ms

NON-WORKING NETWORKS (2):
  CoffeeShop
     Reason: Failed to get IP address | Signal: 45% | Band: 2.4GHz
  PublicWiFi
     Reason: Connection failed | Signal: 38% | Band: 2.4GHz
============================================================
```

## Advanced Features

### Frequency Band Detection
WSS automatically detects and categorizes networks by frequency band:
- **2.4GHz**: Traditional WiFi band (channels 1-13)
- **5GHz**: High-speed band (channels 36-165)
- **6GHz**: WiFi 6E extended band (channels 1-233)

### Signal Quality Analysis
Networks are classified by signal strength:
- **Excellent**: 80-100% signal strength
- **Good**: 60-79% signal strength
- **Weak**: 40-59% signal strength
- **Very Weak**: Below 40% signal strength

### RSSI Measurements
When available, WSS displays Received Signal Strength Indicator (RSSI) values in dBm alongside percentage-based signal strength for more precise signal analysis.

### Ping Statistics
Connection testing includes comprehensive ping analysis:
- Minimum, average, and maximum response times
- Packet loss detection
- Network latency assessment
- Internet connectivity validation

## Data Export

### JSON Format
```json
{
  "timestamp": "2024-01-15T14:30:25.123456",
  "networks": [
    {
      "ssid": "FreeWiFi",
      "security": "",
      "signal": 72,
      "frequency": 5180,
      "band": "5GHz",
      "channel": 36,
      "bssid": "aa:bb:cc:dd:ee:ff",
      "rssi": -45,
      "timestamp": "2024-01-15T14:30:25.123456"
    }
  ],
  "connection_attempts": [
    {
      "ssid": "FreeWiFi",
      "timestamp": "2024-01-15T14:30:30.123456",
      "success": true,
      "ip_address": "192.168.1.100",
      "band": "5GHz",
      "signal": 72,
      "ping_success": true,
      "ping_stats": "min/avg/max = 12.3/15.6/18.9 ms"
    }
  ]
}
```

## Security Considerations

- WSS requires elevated privileges for network interface management
- Only connects to open (unsecured) networks during automated testing
- All connection attempts are logged for security auditing
- Network credentials are never stored or transmitted
- Ping tests use standard ICMP packets to public DNS servers

## Troubleshooting

### Common Issues

**Permission Denied**
```bash
# Run with appropriate privileges
sudo python3 wifi_scanner_suite.py
```

**NetworkManager Not Found**
```bash
# Ensure NetworkManager is installed and running
sudo systemctl status NetworkManager
sudo systemctl start NetworkManager
```

**No Networks Found**
```bash
# Check wireless interface status
ip link show
iwconfig
```

**Connection Failures**
- Verify network interface is not managed by other tools
- Check for conflicting network management services
- Ensure wireless drivers are properly installed

## Development

### Project Structure
```
wifi-scanner-suite/
├── wifi_scanner_suite.py    # Main application
├── README.md                # Documentation
├── LICENSE                  # MIT License
└── wifi_logs/              # Log directory (created automatically)
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Create Pull Request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where applicable
- Include docstrings for all functions and classes
- Maintain backward compatibility

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**OK2HSS**
- Version: 2.0

## Changelog

### Version 2.0
- Added comprehensive connection testing for all open networks
- Implemented detailed reporting with ping statistics
- Enhanced ASCII art banner
- Improved error handling and logging
- Added RSSI measurements and frequency band detection
- Introduced configuration file support

### Version 1.0
- Initial release
- Basic WiFi scanning functionality
- Simple connection testing
- Export capabilities

## Performance Considerations

- Scanning operations may take 10-15 seconds depending on network density
- Connection testing duration varies based on network response times
- Large numbers of open networks will increase total testing time
- Memory usage scales linearly with discovered network count
- Log files are automatically rotated based on age settings

## Supported Platforms

### Tested Distributions
- Ubuntu 18.04, 20.04, 22.04
- Debian 10, 11
- CentOS 7, 8
- Fedora 34, 35, 36
- Arch Linux

### Hardware Requirements
- Wireless network interface
- Minimum 50MB free disk space for logs
- Python 3.7+ runtime environment


### Core Classes

#### WiFiNetwork
Represents a discovered wireless network with the following attributes:
- `ssid`: Network name
- `security`: Security protocol (WPA2, WEP, or empty for open)
- `signal`: Signal strength percentage (0-100)
- `frequency`: Operating frequency in MHz
- `band`: Frequency band (2.4GHz, 5GHz, 6GHz)
- `channel`: WiFi channel number
- `bssid`: MAC address of access point
- `rssi`: Received Signal Strength Indicator in dBm

#### ConnectionAttempt
Records connection attempt results:
- `ssid`: Target network name
- `timestamp`: ISO format timestamp
- `success`: Boolean connection result
- `ip_address`: Assigned IP address (if successful)
- `error_message`: Failure reason (if unsuccessful)
- `ping_success`: Internet connectivity test result
- `ping_stats`: Detailed ping statistics

### Configuration Options

All configuration parameters can be modified in `wifi_config.json`:

#### Network Interface Settings
- `interface`: Default wireless interface (auto-detected if available)

#### Testing Parameters
- `test_host`: Connectivity test target (8.8.8.8 recommended)
- `ping_timeout`: Maximum ping wait time
- `connection_timeout`: Maximum connection attempt duration

#### Logging Configuration
- `log_dir`: Log file storage location
- `max_log_age_days`: Automatic cleanup threshold
- `auto_cleanup`: Enable/disable automatic log rotation

## Disclaimer

This tool is intended for educational and legitimate network testing purposes only. Users are responsible for ensuring compliance with local laws and regulations regarding network scanning and connection testing. The authors assume no liability for misuse of this software.

## Support

For bug reports, feature requests, or general support:
1. Check existing issues on GitHub
2. Create detailed issue reports with system information
3. Include relevant log files and error messages
4. Specify your Linux distribution and version
