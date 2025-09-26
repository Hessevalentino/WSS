# Changelog

All notable changes to WiFi Scanner Suite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.2] - 2025-09-26

### Fixed
- **GitHub URLs**: Updated all repository URLs to correct GitHub address
- **Clone Instructions**: Fixed git clone command with proper repository URL
- **Setup Configuration**: Updated setup.py with correct GitHub repository URL

### Enhanced
- **License Information**: Added comprehensive MIT License section with usage rights
- **Open Source Section**: Added detailed open source information and contribution guidelines
- **Repository Links**: Added direct links to Issues, Releases, and License pages
- **Installation Guide**: Enhanced EXAMPLES.md with quick start installation instructions
- **Community Support**: Improved support section with GitHub issue links

## [2.1.1] - 2025-09-26

### Enhanced
- **BSSID Display**: Added BSSID (MAC address) column to continuous scanning tables
- **Log Viewer Enhancement**: BSSID now displayed in network tables when browsing historical logs
- **Continuous Scanning**: Both Rich and Simple terminal modes now show BSSID information
- **Table Layout**: Improved column ordering for better readability (SSID | Security | Signal | Band | BSSID | Quality/Channel | RSSI)
- **Consistent Formatting**: Unified BSSID display format across all interfaces

### Fixed
- **Column Alignment**: Adjusted table widths to accommodate BSSID column
- **Fallback Display**: Shows "N/A" when BSSID information is unavailable
- **Terminal Compatibility**: BSSID display works in both Rich and simple terminal modes

## [2.1.0] - 2025-09-26

### Added
- **Network Device Discovery**: Comprehensive MAC address scanning of connected devices
- **Multi-method Device Scanning**: ARP table, arp-scan, and nmap fallback methods
- **Device Identification**: Hostname resolution and vendor identification
- **MAC Address Validation**: Robust parsing and validation of MAC addresses
- **Device Deduplication**: Intelligent removal of duplicate devices by MAC address
- **Enhanced JSON Export**: Network devices included in export data structure
- **Advanced Log Viewer**: Browse device information in historical logs
- **Interactive Device Display**: Rich terminal tables for device information
- **Vendor Lookup**: Hardware vendor identification from MAC addresses
- **Device Timestamp Tracking**: Discovery time tracking for each device

### Enhanced
- **Menu System**: Added "Scan Network Devices" option (menu item 3)
- **Log Viewer**: New option to view network devices in historical data
- **JSON Structure**: Extended with `network_devices` array containing device information
- **Error Handling**: Graceful fallback when scanning tools unavailable
- **Documentation**: Updated all documentation with device discovery examples

### Fixed
- **BSSID Parsing**: Resolved issue with truncated MAC addresses in WiFi network data
- **Channel Detection**: Fixed missing channel information in network scans
- **JSON Export**: Eliminated escape sequences in exported data
- **Network Deduplication**: Improved duplicate network detection using SSID+BSSID

### Technical Improvements
- **NetworkDevice Dataclass**: New data structure for device representation
- **Robust nmcli Parsing**: Enhanced parsing with regex validation
- **Frequency-to-Channel Mapping**: Automatic channel calculation from frequency
- **MAC Address Normalization**: Consistent uppercase formatting
- **Multi-tool Integration**: Support for arp-scan, nmap, and ARP table scanning

## [2.0.0] - 2024-01-15

### Added
- Comprehensive connection testing for all open networks
- Detailed connection reports with success/failure analysis
- ASCII art banner with WSS branding
- RSSI (Received Signal Strength Indicator) measurements
- Enhanced frequency band detection (2.4GHz, 5GHz, 6GHz)
- WiFi 6E support with 6GHz band recognition
- Ping statistics with min/avg/max response times
- Configuration file support (wifi_config.json)
- Automatic log rotation and cleanup
- Enhanced error handling and user feedback
- Rich terminal interface support with colors and formatting
- Command-line argument support (--scan, --auto, --continuous, --no-banner)
- Professional documentation suite (README.md, EXAMPLES.md, CONTRIBUTING.md)
- MIT License for open source distribution

### Changed
- Auto-connect functionality now tests all open networks instead of stopping at first success
- Improved network scanning with better frequency parsing
- Enhanced signal quality classification (Excellent, Good, Weak, Very Weak)
- Redesigned menu system with better navigation
- Upgraded export functionality with more detailed data
- Improved connection attempt logging with comprehensive metadata

### Fixed
- WiFi band detection now correctly identifies 2.4GHz, 5GHz, and 6GHz networks
- Signal strength parsing handles various nmcli output formats
- Connection timeout handling prevents indefinite hanging
- Memory usage optimization for large network lists
- Cross-distribution compatibility improvements

### Security
- Added security considerations documentation
- Implemented safe connection testing practices
- Enhanced logging for security audit trails

## [1.0.0] - 2023-12-01

### Added
- Initial release of WiFi Scanner Suite
- Basic WiFi network scanning functionality
- Simple connection testing for open networks
- JSON and CSV export capabilities
- Interactive menu system
- Continuous scanning mode
- Basic logging functionality
- Signal strength measurement
- Network security type detection

### Features
- Real-time WiFi network discovery
- Automated connection attempts
- Export scan results to file
- Cross-platform Linux support
- Command-line interface

## [Unreleased]

### Planned
- WPA/WPA2 network connection support with credential management
- Advanced filtering options (by signal strength, band, security type)
- Network performance benchmarking (speed tests)
- Geolocation integration for site surveys
- REST API for integration with other tools
- Web-based dashboard interface
- Database storage for historical analysis
- Custom notification system for network changes
- Bluetooth and other wireless technology support
- Mobile hotspot detection and analysis

### Under Consideration
- GUI application using tkinter or PyQt
- Network topology mapping
- Interference analysis and channel recommendations
- Integration with network management platforms
- Docker containerization for portable deployment
- Automated report generation and scheduling
- Machine learning for network pattern analysis
- Integration with wardriving databases
- Support for enterprise network authentication
- Custom plugin architecture for extensibility

---

## Version History Summary

- **v2.0.0**: Major feature release with comprehensive testing and professional documentation
- **v1.0.0**: Initial stable release with core functionality

## Migration Guide

### Upgrading from v1.0.0 to v2.0.0

#### Configuration Changes
- Create `wifi_config.json` file for custom settings (optional)
- No breaking changes to existing functionality
- All v1.0.0 features remain available

#### New Dependencies
- `rich` library is now optional but recommended for enhanced interface
- No additional system dependencies required

#### Behavioral Changes
- Auto-connect now tests all networks instead of stopping at first success
- Export format includes additional metadata fields
- Log files include more detailed connection attempt information

#### Command Line Interface
- New arguments: `--no-banner` to skip ASCII art
- Existing arguments remain unchanged and compatible

### Compatibility Notes
- Configuration files from v1.0.0 are not applicable (v1.0.0 had no config file)
- Log files from v1.0.0 remain readable but lack new metadata fields
- Export formats are backward compatible with additional optional fields

## Support and Maintenance

### Long-term Support
- v2.0.x series will receive bug fixes and security updates
- v1.0.x series is now in maintenance mode (critical fixes only)

### End of Life
- v1.0.x support will end 6 months after v2.1.0 release
- Users are encouraged to upgrade to v2.0.x for continued support

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for information about contributing to this project, including how to report bugs, suggest features, and submit code changes.
