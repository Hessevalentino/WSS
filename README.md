# WiFi Scanner Suite (WSS)

A comprehensive command-line WiFi network scanner and connection utility for Linux systems. WSS provides advanced WiFi network discovery, automated connection testing, and detailed reporting capabilities.

## Features

- **Continuous WiFi Scanning**: Real-time monitoring of available wireless networks
- **Network Device Discovery**: Comprehensive MAC address scanning of connected devices
- **Automated Connection Testing**: Systematic testing of open networks with connectivity validation
- **Advanced Network Analysis**: Signal strength, frequency band detection, and RSSI measurements
- **Device Identification**: Hostname resolution and vendor identification for network devices
- **Comprehensive Reporting**: Detailed connection reports with ping statistics and failure analysis
- **JSON Export**: Professional data export with WiFi networks and device information
- **Interactive Menu System**: User-friendly interface with rich terminal support
- **Advanced Log Viewer**: Browse and analyze historical scan data with device information
- **Logging and Statistics**: Persistent storage of scan results, connection attempts, and device data

## Requirements

### System Dependencies
- Linux operating system
- NetworkManager (`nmcli`)
- Wireless tools (`iwconfig`, `iwlist`)
- Network scanning tools (`arp-scan`, `nmap`) - optional for enhanced device discovery
- Python 3.7 or higher

### Python Dependencies
- `rich` (optional, for enhanced terminal interface)

## Installation

### Clone Repository
```bash
git clone https://github.com/Hessevalentino/WSS.git
cd WSS
```

### Install Python Dependencies
```bash
# Optional: Install rich for enhanced interface
pip install rich
```

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt-get install network-manager wireless-tools arp-scan nmap

# CentOS/RHEL/Fedora
sudo yum install NetworkManager wireless-tools arp-scan nmap
# or
sudo dnf install NetworkManager wireless-tools arp-scan nmap

# Note: arp-scan and nmap are optional but recommended for enhanced device discovery
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
3. **Scan Network Devices**: Discover and identify devices connected to the current network
4. **Show Statistics**: Display scan results and connection attempt statistics
5. **Export to JSON**: Save results in JSON format with network and device information
6. **Settings**: View current configuration parameters
7. **Log Viewer**: Browse historical scan data including device information

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
┌─────────────────┬──────────────┬────────┬─────────┬───────────────────┬─────────────┐
│ SSID            │ Security     │ Signal │ Band    │ BSSID             │ Quality     │
├─────────────────┼──────────────┼────────┼─────────┼───────────────────┼─────────────┤
│ HomeNetwork     │ WPA2         │ 85%    │ 2.4GHz  │ AA:BB:CC:DD:EE:FF │ Excellent   │
│ FreeWiFi        │ OPEN         │ 72%    │ 5GHz    │ BB:CC:DD:EE:FF:AA │ Good        │
│ CoffeeShop      │ OPEN         │ 45%    │ 2.4GHz  │ CC:DD:EE:FF:AA:BB │ Weak        │
└─────────────────┴──────────────┴────────┴─────────┴───────────────────┴─────────────┘
```

### Network Device Discovery
```
Found 4 network devices
┌─────────────────┬───────────────────┬──────────────────┬─────────────────┐
│ IP Address      │ MAC Address       │ Hostname         │ Vendor          │
├─────────────────┼───────────────────┼──────────────────┼─────────────────┤
│ 192.168.1.1     │ AA:BB:CC:DD:EE:FF │ router.local     │ Cisco Systems   │
│ 192.168.1.100   │ BB:CC:DD:EE:FF:AA │ laptop           │ Dell Inc.       │
│ 192.168.1.50    │ CC:DD:EE:FF:AA:BB │ -                │ Apple Inc.      │
│ 192.168.1.25    │ DD:EE:FF:AA:BB:CC │ smartphone       │ Samsung         │
└─────────────────┴───────────────────┴──────────────────┴─────────────────┘
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

### BSSID Display
WSS displays BSSID (Basic Service Set Identifier) information for comprehensive network identification:
- **Continuous Scanning**: BSSID shown in real-time network tables
- **Log Viewer**: Historical BSSID data displayed in network browsing
- **Access Point Identification**: Unique MAC addresses for each WiFi access point
- **Network Differentiation**: Distinguish between multiple APs with same SSID

### RSSI Measurements
When available, WSS displays Received Signal Strength Indicator (RSSI) values in dBm alongside percentage-based signal strength for more precise signal analysis.

### Network Device Discovery
WSS provides comprehensive device discovery capabilities:
- **ARP Table Scanning**: Fast discovery of known devices
- **Active Network Scanning**: Using arp-scan for complete network mapping
- **Vendor Identification**: MAC address vendor lookup for device identification
- **Hostname Resolution**: Device name discovery when available
- **Multiple Scan Methods**: Fallback to nmap when specialized tools unavailable

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
  ],
  "network_devices": [
    {
      "ip_address": "192.168.1.1",
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "hostname": "router.local",
      "vendor": "Cisco Systems",
      "timestamp": "2024-01-15T14:30:25.123456"
    },
    {
      "ip_address": "192.168.1.100",
      "mac_address": "BB:CC:DD:EE:FF:AA",
      "hostname": "laptop",
      "vendor": "Dell Inc.",
      "timestamp": "2024-01-15T14:30:25.123456"
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
- Contact: [Your contact information]

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

## API Reference

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

#### NetworkDevice
Represents a discovered network device with the following attributes:
- `ip_address`: Device IP address in the network
- `mac_address`: Hardware MAC address (unique identifier)
- `hostname`: Device hostname (if resolvable)
- `vendor`: Network interface vendor (from MAC address lookup)
- `timestamp`: ISO format discovery timestamp

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

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### MIT License Summary
- ✅ **Commercial use** - Use in commercial projects
- ✅ **Modification** - Modify and adapt the code
- ✅ **Distribution** - Share and distribute freely
- ✅ **Private use** - Use for personal projects
- ❗ **Liability** - No warranty provided
- ❗ **Attribution** - Must include original license

## Open Source

WiFi Scanner Suite is **100% open source** and welcomes contributions from the community!

### 🌟 **Why Open Source?**
- **Transparency** - Full code visibility for security auditing
- **Community-driven** - Improvements from developers worldwide
- **Educational** - Learn from real-world networking code
- **Customizable** - Adapt to your specific needs
- **Free forever** - No licensing fees or restrictions

### 🤝 **Contributing**
We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines:
- 🐛 **Bug reports** - Help us identify and fix issues
- 💡 **Feature requests** - Suggest new functionality
- 🔧 **Code contributions** - Submit pull requests
- 📚 **Documentation** - Improve guides and examples
- 🧪 **Testing** - Help test on different systems

### 📊 **Project Stats**
- **Language:** Python 3.7+
- **Dependencies:** Minimal (only `rich` optional)
- **Platform:** Linux (NetworkManager required)
- **License:** MIT (Commercial-friendly)
- **Maintenance:** Actively maintained

### 🔗 **Links**
- **Repository:** [https://github.com/Hessevalentino/WSS](https://github.com/Hessevalentino/WSS)
- **Issues:** [https://github.com/Hessevalentino/WSS/issues](https://github.com/Hessevalentino/WSS/issues)
- **Releases:** [https://github.com/Hessevalentino/WSS/releases](https://github.com/Hessevalentino/WSS/releases)
- **License:** [https://github.com/Hessevalentino/WSS/blob/main/LICENSE](https://github.com/Hessevalentino/WSS/blob/main/LICENSE)

## Support

For bug reports, feature requests, or general support:
1. **Check existing issues** on [GitHub Issues](https://github.com/Hessevalentino/WSS/issues)
2. **Create detailed issue reports** with system information
3. **Include relevant log files** and error messages
4. **Specify your Linux distribution** and version
5. **Star the repository** ⭐ if you find it useful!

---

<div align="center">

**Made with ❤️ by [OK2HSS](https://github.com/Hessevalentino)**

*If this project helped you, please consider giving it a ⭐ on GitHub!*

</div>
