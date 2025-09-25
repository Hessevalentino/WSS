# Changelog

All notable changes to WiFi Scanner Suite will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
