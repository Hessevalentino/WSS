#!/usr/bin/env python3
"""
WSS - WiFi Scanner Suite
Author: OK2HSS
Version: 2.1.1

Features:
- Continuous WiFi scanning with BSSID display
- Auto-connect to open networks
- Network device discovery and MAC scanning
- Advanced log viewer with BSSID information
- Export to JSON with device data
- Interactive menu
"""

import subprocess
import json
import time
import re
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple
from pathlib import Path
import argparse

# Rich library for beautiful terminal interface
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.prompt import Prompt
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️  For better appearance install rich: pip install rich")

@dataclass
class WiFiNetwork:
    """WiFi network representation"""
    ssid: str
    security: str
    signal: int
    frequency: int
    band: str
    channel: Optional[int] = None
    bssid: Optional[str] = None
    rssi: Optional[int] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

        # Determine band based on frequency (MHz)
        if self.frequency and self.frequency > 0:
            if 2400 <= self.frequency <= 2500:
                self.band = "2.4GHz"
            elif 5000 <= self.frequency <= 6000:
                self.band = "5GHz"
            elif self.frequency >= 6000:
                self.band = "6GHz"
            else:
                self.band = "Unknown"
        else:
            self.band = "Unknown"

    @property
    def is_open(self) -> bool:
        """Returns True if network is open"""
        return not self.security or self.security.strip() == ""

    @property
    def signal_quality(self) -> str:
        """Returns text description of signal quality"""
        if self.signal >= 80:
            return "Excellent"
        elif self.signal >= 60:
            return "Good"
        elif self.signal >= 40:
            return "Weak"
        else:
            return "Very weak"

@dataclass
class NetworkDevice:
    """Network device representation"""
    ip_address: str
    mac_address: str
    hostname: Optional[str] = None
    vendor: Optional[str] = None
    timestamp: Optional[str] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

@dataclass
class ConnectionAttempt:
    """Connection attempt representation"""
    ssid: str
    timestamp: str
    success: bool
    ip_address: Optional[str] = None
    error_message: Optional[str] = None
    band: Optional[str] = None
    signal: Optional[int] = None
    ping_success: Optional[bool] = None
    ping_stats: Optional[str] = None

def show_ascii_banner():
    """Display ASCII art banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██╗    ██╗███████╗███████╗                                                  ║
║  ██║    ██║██╔════╝██╔════╝                                                  ║
║  ██║ █╗ ██║███████╗███████╗                                                  ║
║  ██║███╗██║╚════██║╚════██║                                                  ║
║  ╚███╔███╔╝███████║███████║                                                  ║
║   ╚══╝╚══╝ ╚══════╝╚══════╝                                                  ║
║                                                                              ║
║                    ╦ ╦┬┌─┐┬   ╔═╗┌─┐┌─┐┌┐┌┌┐┌┌─┐┬─┐  ╔═╗┬ ┬┬┌┬┐┌─┐          ║
║                    ║║║│├┤ │   ╚═╗│  ├─┤││││││├┤ ├┬┘  ╚═╗│ ││ │ ├┤           ║
║                    ╚╩╝┴└  ┴   ╚═╝└─┘┴ ┴┘└┘┘└┘└─┘┴└─  ╚═╝└─┘┴ ┴ └─┘          ║
║                                                                              ║
║                           Author: OK2HSS | Version: 2.0                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    return banner

def show_ascii_banner_simple():
    """Display simple ASCII art banner for terminals without rich"""
    banner = """
================================================================================

    ██╗    ██╗███████╗███████╗
    ██║    ██║██╔════╝██╔════╝
    ██║ █╗ ██║███████╗███████╗
    ██║███╗██║╚════██║╚════██║
    ╚███╔███╔╝███████║███████║
     ╚══╝╚══╝ ╚══════╝╚══════╝

              WiFi Scanner Suite
              Author: OK2HSS | Version: 2.0

================================================================================
    """
    return banner

class WiFiConfig:
    """Application configuration"""
    def __init__(self, config_file: str = "wifi_config.json"):
        self.config_file = Path(config_file)
        self.default_config = {
            "interface": "wlan0",
            "test_host": "8.8.8.8",
            "scan_interval": 10,
            "log_dir": "./wifi_logs",
            "max_log_age_days": 30,
            "ping_timeout": 5,
            "connection_timeout": 15,
            "auto_cleanup": True,
            "export_format": "json"
        }
        self.config = self.load_config()

    def load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.default_config, **json.load(f)}
            except Exception as e:
                print(f"⚠️  Error loading configuration: {e}")

        return self.default_config.copy()

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def get(self, key: str, default=None):
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        self.config[key] = value

class WiFiScanner:
    """Main class for WiFi scanning"""

    def __init__(self, config: WiFiConfig):
        self.config = config
        self.console = Console() if RICH_AVAILABLE else None
        self.log_dir = Path(self.config.get("log_dir"))
        self.log_dir.mkdir(exist_ok=True)

        # Lists for storing data
        self.discovered_networks: List[WiFiNetwork] = []
        self.connection_attempts: List[ConnectionAttempt] = []
        self.discovered_devices: List[NetworkDevice] = []

    def run_command(self, cmd: str, timeout: int = 30) -> Tuple[bool, str]:
        """Execute system command"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True,
                text=True, timeout=timeout
            )
            return result.returncode == 0, result.stdout
        except subprocess.TimeoutExpired:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)

    def check_dependencies(self) -> bool:
        """Check system dependencies"""
        dependencies = ['nmcli', 'ping', 'iwconfig']
        missing = []

        for dep in dependencies:
            success, _ = self.run_command(f"which {dep}")
            if not success:
                missing.append(dep)

        if missing:
            print(f"❌ Missing dependencies: {', '.join(missing)}")
            return False

        return True
    
    def scan_networks(self) -> List[WiFiNetwork]:
        """Scan available WiFi networks"""
        # Start rescan
        self.run_command("nmcli device wifi rescan", timeout=15)
        time.sleep(2)

        # Get network list with detailed information
        # First try to get RSSI with iwlist, fallback to nmcli
        rssi_data = {}
        rssi_success, rssi_output = self.run_command(
            f"iwlist {self.config.get('interface')} scan | grep -E 'ESSID|Signal level'"
        )

        if rssi_success:
            current_ssid = None
            for line in rssi_output.split('\n'):
                if 'ESSID:' in line:
                    current_ssid = line.split('ESSID:')[1].strip().strip('"')
                elif 'Signal level=' in line and current_ssid:
                    try:
                        rssi = int(line.split('Signal level=')[1].split(' ')[0])
                        rssi_data[current_ssid] = rssi
                    except:
                        pass

        # Get basic network list from nmcli
        success, output = self.run_command(
            "nmcli -t -f SSID,SECURITY,SIGNAL,FREQ,BSSID,CHAN device wifi list"
        )

        if not success:
            return []

        networks = []
        for line in output.strip().split('\n'):
            # Use robust parsing method
            parsed_data = self._parse_nmcli_line_robust(line)
            if not parsed_data:
                continue

            ssid = parsed_data['ssid']
            if not ssid:  # Skip empty SSID
                continue

            # Get RSSI if available
            rssi = rssi_data.get(ssid, None)

            network = WiFiNetwork(
                ssid=ssid,
                security=parsed_data['security'],
                signal=parsed_data['signal'],
                frequency=parsed_data['frequency'],
                band="Unknown",  # Will be determined in __post_init__
                channel=parsed_data['channel'],
                bssid=parsed_data['bssid'],
                rssi=rssi
            )
            networks.append(network)

        # Add only new networks to discovered networks list (deduplicate by SSID+BSSID)
        self._add_unique_networks(networks)
        return networks

    def _add_unique_networks(self, new_networks: List[WiFiNetwork]):
        """Add only unique networks to discovered_networks list"""
        # Create a set of existing network identifiers (SSID + BSSID combination)
        existing_networks = set()
        for network in self.discovered_networks:
            # Use SSID + BSSID as unique identifier (BSSID is MAC address of access point)
            identifier = f"{network.ssid}|{network.bssid or 'no_bssid'}"
            existing_networks.add(identifier)

        # Add only networks that don't already exist
        for network in new_networks:
            identifier = f"{network.ssid}|{network.bssid or 'no_bssid'}"
            if identifier not in existing_networks:
                self.discovered_networks.append(network)
                existing_networks.add(identifier)  # Update set for next iterations

    def _validate_bssid(self, bssid: str) -> Optional[str]:
        """Validate and clean BSSID format"""
        if not bssid:
            return None

        # Remove any escape characters or extra backslashes
        bssid = bssid.replace('\\', '').strip()

        # Check if it's a valid MAC address format
        mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
        if mac_pattern.match(bssid):
            return bssid.upper()  # Normalize to uppercase

        # Check if it's a partial MAC (just first part)
        partial_pattern = re.compile(r'^[0-9A-Fa-f]{2}$')
        if partial_pattern.match(bssid):
            # This is likely a parsing error - return None to indicate invalid
            return None

        return None

    def _parse_nmcli_line_robust(self, line: str) -> Optional[dict]:
        """Robustly parse nmcli output line with proper BSSID handling"""
        if not line.strip():
            return None

        # Split by colon, but be smart about BSSID
        parts = line.split(':')

        # We expect at least SSID:SECURITY:SIGNAL:FREQ:BSSID_PART1:...:BSSID_PART6:CHAN
        # That's minimum 8 parts (SSID, SECURITY, SIGNAL, FREQ, 6 BSSID parts, CHAN)
        if len(parts) < 8:
            return None

        try:
            ssid = parts[0].strip()
            security = parts[1].strip()
            signal_str = parts[2].strip()
            freq_str = parts[3].strip()

            # Reconstruct BSSID from parts[4] to parts[9] (6 parts)
            bssid_parts = parts[4:10]  # Take 6 parts for BSSID
            bssid_raw = ':'.join(bssid_parts)

            # Channel is the part after BSSID
            channel_str = parts[10] if len(parts) > 10 else ""

            # Validate and clean BSSID
            bssid = self._validate_bssid(bssid_raw)

            # Parse signal
            signal = int(signal_str) if signal_str.isdigit() else 0

            # Parse frequency
            freq = self._parse_frequency(freq_str)

            # Parse channel
            channel = self._parse_channel(channel_str, freq)

            return {
                'ssid': ssid,
                'security': security,
                'signal': signal,
                'frequency': freq,
                'bssid': bssid,
                'channel': channel
            }

        except (ValueError, IndexError) as e:
            # Log parsing error for debugging
            print(f"⚠️  Parsing error for line: {line[:50]}... - {e}")
            return None

    def _parse_frequency(self, freq_str: str) -> int:
        """Parse frequency string to MHz"""
        if not freq_str:
            return 0

        try:
            # Clean frequency string
            freq_clean = freq_str.replace('MHz', '').replace('GHz', '').replace(' ', '').strip()

            if '.' in freq_clean:
                # Handle "2.412" format (GHz) - convert to MHz
                return int(float(freq_clean) * 1000)
            else:
                # Handle "2412" format (MHz)
                return int(freq_clean)
        except ValueError:
            return 0

    def _parse_channel(self, channel_str: str, frequency: int) -> Optional[int]:
        """Parse channel number with frequency-based fallback"""
        # Try direct parsing first
        if channel_str and channel_str.isdigit():
            return int(channel_str)

        # Fallback: calculate channel from frequency
        if frequency > 0:
            return self._frequency_to_channel(frequency)

        return None

    def _frequency_to_channel(self, frequency: int) -> Optional[int]:
        """Convert frequency to WiFi channel number"""
        # 2.4GHz band channels
        if 2412 <= frequency <= 2484:
            if frequency == 2484:
                return 14
            else:
                return (frequency - 2412) // 5 + 1

        # 5GHz band channels (simplified mapping)
        elif 5000 <= frequency <= 6000:
            # Common 5GHz channels
            freq_to_chan_5g = {
                5180: 36, 5200: 40, 5220: 44, 5240: 48,
                5260: 52, 5280: 56, 5300: 60, 5320: 64,
                5500: 100, 5520: 104, 5540: 108, 5560: 112,
                5580: 116, 5600: 120, 5620: 124, 5640: 128,
                5660: 132, 5680: 136, 5700: 140, 5720: 144,
                5745: 149, 5765: 153, 5785: 157, 5805: 161,
                5825: 165
            }
            return freq_to_chan_5g.get(frequency)

        return None

    def scan_network_devices(self) -> List[NetworkDevice]:
        """Scan for devices in the current network using ARP and arp-scan"""
        devices = []

        # Method 1: Use ARP table
        devices.extend(self._scan_arp_table())

        # Method 2: Use arp-scan if available
        arp_scan_devices = self._scan_with_arp_scan()
        if arp_scan_devices:
            devices.extend(arp_scan_devices)

        # Method 3: Use nmap as fallback
        if not devices:
            devices.extend(self._scan_with_nmap())

        # Deduplicate devices by MAC address
        unique_devices = self._deduplicate_devices(devices)

        # Add to discovered devices list
        self.discovered_devices.extend(unique_devices)

        return unique_devices

    def _scan_arp_table(self) -> List[NetworkDevice]:
        """Scan ARP table for known devices"""
        devices = []

        # Get ARP table
        success, output = self.run_command("arp -a")
        if not success:
            return devices

        for line in output.strip().split('\n'):
            if not line or 'incomplete' in line.lower():
                continue

            # Parse ARP line: hostname (ip) at mac [ether] on interface
            # Example: router.local (192.168.1.1) at aa:bb:cc:dd:ee:ff [ether] on wlan0
            match = re.search(r'(\S+)\s*\(([0-9.]+)\)\s+at\s+([a-fA-F0-9:]{17})', line)
            if match:
                hostname, ip, mac = match.groups()

                # Clean hostname
                if hostname == '?':
                    hostname = None

                device = NetworkDevice(
                    ip_address=ip,
                    mac_address=mac.upper(),
                    hostname=hostname
                )
                devices.append(device)

        return devices

    def _scan_with_arp_scan(self) -> List[NetworkDevice]:
        """Scan network using arp-scan tool"""
        devices = []

        # Check if arp-scan is available
        success, _ = self.run_command("which arp-scan")
        if not success:
            return devices

        # Get current network interface
        interface = self.config.get('interface')

        # Run arp-scan on local network
        success, output = self.run_command(f"sudo arp-scan -l -I {interface}", timeout=30)
        if not success:
            # Try without sudo
            success, output = self.run_command(f"arp-scan -l -I {interface}", timeout=30)
            if not success:
                return devices

        for line in output.strip().split('\n'):
            if not line or line.startswith('Interface:') or line.startswith('Starting'):
                continue

            # Parse arp-scan line: IP MAC VENDOR
            # Example: 192.168.1.1    aa:bb:cc:dd:ee:ff    Cisco Systems
            parts = line.split('\t')
            if len(parts) >= 2:
                ip = parts[0].strip()
                mac = parts[1].strip()
                vendor = parts[2].strip() if len(parts) > 2 else None

                # Validate IP and MAC format
                if re.match(r'^[0-9.]+$', ip) and re.match(r'^[a-fA-F0-9:]{17}$', mac):
                    device = NetworkDevice(
                        ip_address=ip,
                        mac_address=mac.upper(),
                        vendor=vendor
                    )
                    devices.append(device)

        return devices

    def _scan_with_nmap(self) -> List[NetworkDevice]:
        """Scan network using nmap as fallback"""
        devices = []

        # Check if nmap is available
        success, _ = self.run_command("which nmap")
        if not success:
            return devices

        # Get current network range
        success, output = self.run_command("ip route | grep -E 'wlan0|eth0' | grep -v default | head -1")
        if not success:
            return devices

        # Extract network range (e.g., 192.168.1.0/24)
        network_match = re.search(r'([0-9.]+/[0-9]+)', output)
        if not network_match:
            return devices

        network = network_match.group(1)

        # Run nmap ping scan
        success, output = self.run_command(f"nmap -sn {network}", timeout=60)
        if not success:
            return devices

        # Parse nmap output for MAC addresses
        current_ip = None
        for line in output.strip().split('\n'):
            # Look for IP addresses
            ip_match = re.search(r'Nmap scan report for ([0-9.]+)', line)
            if ip_match:
                current_ip = ip_match.group(1)
                continue

            # Look for MAC addresses
            if current_ip and 'MAC Address:' in line:
                mac_match = re.search(r'MAC Address: ([a-fA-F0-9:]{17})', line)
                if mac_match:
                    mac = mac_match.group(1)

                    # Extract vendor if available
                    vendor_match = re.search(r'\(([^)]+)\)', line)
                    vendor = vendor_match.group(1) if vendor_match else None

                    device = NetworkDevice(
                        ip_address=current_ip,
                        mac_address=mac.upper(),
                        vendor=vendor
                    )
                    devices.append(device)
                    current_ip = None  # Reset for next device

        return devices

    def _deduplicate_devices(self, devices: List[NetworkDevice]) -> List[NetworkDevice]:
        """Remove duplicate devices based on MAC address"""
        seen_macs = set()
        unique_devices = []

        for device in devices:
            if device.mac_address not in seen_macs:
                unique_devices.append(device)
                seen_macs.add(device.mac_address)

        return unique_devices

    def connect_to_network(self, ssid: str) -> ConnectionAttempt:
        """Attempt to connect to network"""
        attempt = ConnectionAttempt(
            ssid=ssid,
            timestamp=datetime.now().isoformat(),
            success=False
        )

        # Disconnect from current network
        self.run_command(f"nmcli device disconnect {self.config.get('interface')}")
        time.sleep(2)

        # Connect to network
        success, output = self.run_command(
            f"nmcli device wifi connect '{ssid}'",
            timeout=self.config.get('connection_timeout')
        )

        if not success:
            attempt.error_message = f"Connection failed: {output}"
            return attempt

        # Wait for IP address
        time.sleep(5)

        # Get IP address
        success, ip_output = self.run_command(
            f"ip route get {self.config.get('test_host')} | grep -oP 'src \\K\\S+'"
        )

        if success and ip_output.strip():
            attempt.ip_address = ip_output.strip()

            # Test ping
            ping_success, _ = self.run_command(
                f"ping -c 3 -W {self.config.get('ping_timeout')} {self.config.get('test_host')}"
            )
            attempt.ping_success = ping_success
            attempt.success = ping_success
        else:
            attempt.error_message = "Failed to get IP address"

        self.connection_attempts.append(attempt)
        return attempt

    def connect_to_network_enhanced(self, network: WiFiNetwork) -> ConnectionAttempt:
        """Enhanced connection attempt with detailed ping statistics"""
        attempt = ConnectionAttempt(
            ssid=network.ssid,
            timestamp=datetime.now().isoformat(),
            success=False,
            band=network.band,
            signal=network.signal
        )

        # Disconnect from current network
        self.run_command(f"nmcli device disconnect {self.config.get('interface')}")
        time.sleep(2)

        # Connect to network
        success, output = self.run_command(
            f"nmcli device wifi connect '{network.ssid}'",
            timeout=self.config.get('connection_timeout')
        )

        if not success:
            attempt.error_message = f"Connection failed: {output.strip()}"
            self.connection_attempts.append(attempt)
            return attempt

        # Wait for IP address
        time.sleep(5)

        # Get IP address
        success, ip_output = self.run_command(
            f"ip route get {self.config.get('test_host')} | grep -oP 'src \\K\\S+'"
        )

        if success and ip_output.strip():
            attempt.ip_address = ip_output.strip()

            # Enhanced ping test with statistics
            ping_success, ping_output = self.run_command(
                f"ping -c 4 -W {self.config.get('ping_timeout')} {self.config.get('test_host')}"
            )

            attempt.ping_success = ping_success

            if ping_success and ping_output:
                # Parse ping statistics
                try:
                    lines = ping_output.strip().split('\n')
                    for line in lines:
                        if 'rtt min/avg/max/mdev' in line or 'round-trip' in line:
                            # Extract ping times: "rtt min/avg/max/mdev = 12.345/23.456/34.567/5.678 ms"
                            stats_part = line.split('=')[1].strip() if '=' in line else ""
                            if stats_part:
                                times = stats_part.split('/')[0:3]  # min/avg/max
                                if len(times) >= 3:
                                    attempt.ping_stats = f"min/avg/max = {times[0]}/{times[1]}/{times[2]} ms"
                                    break
                        elif 'packet loss' in line:
                            # Extract packet loss info
                            if '0% packet loss' in line:
                                if not hasattr(attempt, 'ping_stats'):
                                    attempt.ping_stats = "0% packet loss"
                            else:
                                loss_info = line.split(',')[-2].strip() if ',' in line else line
                                if not hasattr(attempt, 'ping_stats'):
                                    attempt.ping_stats = loss_info
                except Exception:
                    # If parsing fails, just mark as successful
                    attempt.ping_stats = "Ping successful"

            attempt.success = ping_success
        else:
            attempt.error_message = "Failed to get IP address"

        self.connection_attempts.append(attempt)
        return attempt
    
    def continuous_scan(self):
        """Continuous scanning"""
        if not RICH_AVAILABLE:
            return self._continuous_scan_simple()

        return self._continuous_scan_rich()

    def _continuous_scan_simple(self):
        """Simple continuous scanning without rich"""
        scan_count = 0
        try:
            while True:
                scan_count += 1
                print(f"\n{'='*50}")
                print(f"Scan #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
                print(f"{'='*50}")

                networks = self.scan_networks()
                open_networks = [n for n in networks if n.is_open]

                band_24_simple = [n for n in networks if n.band == "2.4GHz"]
                band_5_simple = [n for n in networks if n.band == "5GHz"]
                band_6_simple = [n for n in networks if n.band == "6GHz"]

                print(f"📡 Total networks: {len(networks)}")
                print(f"🔓 Open networks: {len(open_networks)}")
                print(f"📡 2.4GHz: {len(band_24_simple)}")
                print(f"⚡ 5GHz: {len(band_5_simple)}")
                print(f"🚀 6GHz: {len(band_6_simple)}")

                if open_networks:
                    print("\n🎉 OPEN NETWORKS FOUND:")
                    for net in open_networks:
                        band_display = net.band if net.band else "Unknown"
                        rssi_display = f" ({net.rssi}dBm)" if net.rssi else ""
                        bssid_display = f" | BSSID: {net.bssid}" if net.bssid else ""
                        print(f"  → \033[92m{net.ssid}\033[0m ({net.signal}%{rssi_display} {band_display}){bssid_display} \033[92m[OPEN]\033[0m")

                print(f"\nWaiting {self.config.get('scan_interval')}s...")
                time.sleep(self.config.get('scan_interval'))

        except KeyboardInterrupt:
            print("\n\nScanning terminated by user.")
    
    def _continuous_scan_rich(self):
        """Advanced continuous scanning with rich"""
        scan_count = 0

        try:
            while True:
                scan_count += 1

                # Scanning
                with self.console.status("[bold green]Scanning WiFi networks..."):
                    networks = self.scan_networks()

                # Statistics
                open_networks = [n for n in networks if n.is_open]
                band_24 = [n for n in networks if n.band == "2.4GHz"]
                band_5 = [n for n in networks if n.band == "5GHz"]
                band_6 = [n for n in networks if n.band == "6GHz"]
                unknown_bands = [n for n in networks if n.band.startswith("Unknown")]

                # Create table
                table = Table(title=f"WiFi Scan #{scan_count} - {datetime.now().strftime('%H:%M:%S')}")
                table.add_column("SSID", style="cyan")
                table.add_column("Security")
                table.add_column("Signal", style="green")
                table.add_column("Band", style="magenta")
                table.add_column("BSSID", style="dim")
                table.add_column("Quality", style="yellow")

                # Sort by signal strength
                networks_sorted = sorted(networks, key=lambda x: x.signal, reverse=True)

                for network in networks_sorted[:15]:  # Show only top 15
                    # Color coding for security
                    if network.is_open:
                        security_display = "[bold green]🔓 OPEN[/bold green]"
                        ssid_style = "[bold green]"
                        ssid_display = f"{ssid_style}{network.ssid}[/bold green]"
                    else:
                        security_display = f"[red]🔒 {network.security}[/red]"
                        ssid_display = network.ssid

                    # Enhanced signal display with RSSI
                    if network.rssi:
                        signal_display = f"{network.signal}% ({network.rssi}dBm)"
                    else:
                        signal_display = f"{network.signal}%"

                    band_display = network.band if network.band else "Unknown"
                    bssid_display = network.bssid if network.bssid else "N/A"

                    table.add_row(
                        ssid_display,
                        security_display,
                        signal_display,
                        band_display,
                        bssid_display,
                        network.signal_quality
                    )
                
                # Statistics panel
                stats_text = f"""
📊 [bold]Statistics:[/bold]
  • Total networks: [bold blue]{len(networks)}[/bold blue]
  • 🔓 Open: [bold green]{len(open_networks)}[/bold green]
  • 📡 2.4GHz: [bold cyan]{len(band_24)}[/bold cyan]
  • ⚡ 5GHz: [bold magenta]{len(band_5)}[/bold magenta]
  • 🚀 6GHz: [bold yellow]{len(band_6)}[/bold yellow]
"""

                if unknown_bands:
                    stats_text += f"  • ❓ Unknown: [bold red]{len(unknown_bands)}[/bold red]\n"

                if open_networks:
                    stats_text += f"\n🎉 [bold yellow]FOUND {len(open_networks)} OPEN NETWORKS![/bold yellow]"

                stats_panel = Panel(stats_text, title="📈 Overview", border_style="green")

                # Display
                self.console.clear()
                self.console.print(table)
                self.console.print(stats_panel)

                # Progress bar countdown
                scan_interval = self.config.get('scan_interval')
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[bold blue]Waiting for next scan..."),
                    BarColumn(),
                    TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                    TimeRemainingColumn(),
                    console=self.console
                ) as progress:
                    task = progress.add_task("countdown", total=scan_interval)
                    for _ in range(scan_interval):
                        time.sleep(1)
                        progress.update(task, advance=1)

        except KeyboardInterrupt:
            self.console.print("\n\n[yellow]Scanning terminated by user.[/yellow]")
    
    def auto_connect(self):
        """Automatic connection to open networks"""
        if RICH_AVAILABLE:
            self.console.print("[bold cyan]🔍 Scanning for WiFi networks...[/bold cyan]")
        else:
            print("🔍 Scanning for WiFi networks...")

        networks = self.scan_networks()
        open_networks = [n for n in networks if n.is_open]

        if not open_networks:
            if RICH_AVAILABLE:
                self.console.print("[red]❌ No open networks found[/red]")
            else:
                print("❌ No open networks found")
            return

        # Sort by signal strength
        open_networks.sort(key=lambda x: x.signal, reverse=True)

        if RICH_AVAILABLE:
            self.console.print(f"[green]🔍 Found {len(open_networks)} open networks[/green]")

            # Show available networks
            self.console.print("\n[bold]Available open networks:[/bold]")
            for i, net in enumerate(open_networks[:5], 1):
                rssi_info = f" ({net.rssi}dBm)" if net.rssi else ""
                self.console.print(f"  {i}. [green]{net.ssid}[/green] - {net.signal}%{rssi_info} [{net.band}]")
        else:
            print(f"🔍 Found {len(open_networks)} open networks")
            print("\nAvailable open networks:")
            for i, net in enumerate(open_networks[:5], 1):
                rssi_info = f" ({net.rssi}dBm)" if net.rssi else ""
                print(f"  {i}. {net.ssid} - {net.signal}%{rssi_info} [{net.band}]")

        print()  # Empty line for better readability

        for i, network in enumerate(open_networks, 1):
            # Show which network we're trying
            if RICH_AVAILABLE:
                self.console.print(f"[bold blue]🔄 [{i}/{len(open_networks)}] Attempting to connect to: [cyan]{network.ssid}[/cyan][/bold blue]")
                self.console.print(f"   Signal: {network.signal}% | Band: {network.band} | BSSID: {network.bssid or 'N/A'}")
            else:
                print(f"🔄 [{i}/{len(open_networks)}] Attempting to connect to: {network.ssid}")
                print(f"   Signal: {network.signal}% | Band: {network.band} | BSSID: {network.bssid or 'N/A'}")

            attempt = self.connect_to_network_enhanced(network)

            # Brief status update during testing
            if attempt.success:
                if RICH_AVAILABLE:
                    self.console.print(f"[green]   ✅ Connected successfully[/green]")
                else:
                    print(f"   ✅ Connected successfully")
            else:
                if RICH_AVAILABLE:
                    self.console.print(f"[red]   ❌ Failed: {attempt.error_message}[/red]")
                else:
                    print(f"   ❌ Failed: {attempt.error_message}")

            print()  # Empty line between attempts

        # Show comprehensive report after testing all networks
        self.show_connection_report(open_networks)

    def show_connection_report(self, tested_networks: List[WiFiNetwork]):
        """Show comprehensive report of all connection attempts"""
        if not tested_networks:
            return

        # Get recent connection attempts for these networks
        recent_attempts = []
        for network in tested_networks:
            # Find the most recent attempt for this network
            network_attempts = [a for a in self.connection_attempts if a.ssid == network.ssid]
            if network_attempts:
                recent_attempts.append(network_attempts[-1])  # Most recent attempt

        successful_attempts = [a for a in recent_attempts if a.success]
        failed_attempts = [a for a in recent_attempts if not a.success]

        if RICH_AVAILABLE:
            self.console.print("\n" + "="*60)
            self.console.print("[bold cyan]📊 CONNECTION REPORT[/bold cyan]")
            self.console.print("="*60)

            # Summary
            self.console.print(f"\n[bold]Summary:[/bold]")
            self.console.print(f"  • Total networks tested: [blue]{len(tested_networks)}[/blue]")
            self.console.print(f"  • ✅ Successful connections: [green]{len(successful_attempts)}[/green]")
            self.console.print(f"  • ❌ Failed connections: [red]{len(failed_attempts)}[/red]")

            # Successful connections
            if successful_attempts:
                self.console.print(f"\n[bold green]✅ WORKING NETWORKS ({len(successful_attempts)}):[/bold green]")
                for attempt in successful_attempts:
                    network = next((n for n in tested_networks if n.ssid == attempt.ssid), None)
                    if network:
                        ping_info = ""
                        if hasattr(attempt, 'ping_stats') and attempt.ping_stats:
                            ping_info = f" | Ping: {attempt.ping_stats}"
                        elif attempt.ping_success:
                            ping_info = " | Ping: ✅ Success"

                        self.console.print(f"  🌐 [bold green]{attempt.ssid}[/bold green]")
                        self.console.print(f"     IP: {attempt.ip_address} | Signal: {network.signal}% | Band: {network.band}{ping_info}")

            # Failed connections
            if failed_attempts:
                self.console.print(f"\n[bold red]❌ NON-WORKING NETWORKS ({len(failed_attempts)}):[/bold red]")
                for attempt in failed_attempts:
                    network = next((n for n in tested_networks if n.ssid == attempt.ssid), None)
                    if network:
                        self.console.print(f"  📵 [bold red]{attempt.ssid}[/bold red]")
                        self.console.print(f"     Reason: {attempt.error_message} | Signal: {network.signal}% | Band: {network.band}")

            self.console.print("\n" + "="*60)

        else:
            print("\n" + "="*60)
            print("📊 CONNECTION REPORT")
            print("="*60)

            # Summary
            print(f"\nSummary:")
            print(f"  • Total networks tested: {len(tested_networks)}")
            print(f"  • ✅ Successful connections: {len(successful_attempts)}")
            print(f"  • ❌ Failed connections: {len(failed_attempts)}")

            # Successful connections
            if successful_attempts:
                print(f"\n✅ WORKING NETWORKS ({len(successful_attempts)}):")
                for attempt in successful_attempts:
                    network = next((n for n in tested_networks if n.ssid == attempt.ssid), None)
                    if network:
                        ping_info = ""
                        if hasattr(attempt, 'ping_stats') and attempt.ping_stats:
                            ping_info = f" | Ping: {attempt.ping_stats}"
                        elif attempt.ping_success:
                            ping_info = " | Ping: ✅ Success"

                        print(f"  🌐 {attempt.ssid}")
                        print(f"     IP: {attempt.ip_address} | Signal: {network.signal}% | Band: {network.band}{ping_info}")

            # Failed connections
            if failed_attempts:
                print(f"\n❌ NON-WORKING NETWORKS ({len(failed_attempts)}):")
                for attempt in failed_attempts:
                    network = next((n for n in tested_networks if n.ssid == attempt.ssid), None)
                    if network:
                        print(f"  📵 {attempt.ssid}")
                        print(f"     Reason: {attempt.error_message} | Signal: {network.signal}% | Band: {network.band}")

            print("\n" + "="*60)

    def save_logs(self):
        """Save logs to JSON file with unique networks only"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"wifi_scan_{timestamp}.json"

        # Final deduplicate networks before saving (extra safety)
        unique_networks = self._get_unique_networks_for_export()

        data = {
            "timestamp": datetime.now().isoformat(),
            "networks": [asdict(n) for n in unique_networks],
            "connection_attempts": [asdict(a) for a in self.connection_attempts],
            "network_devices": [asdict(d) for d in self.discovered_devices]
        }

        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return log_file

    def _get_unique_networks_for_export(self) -> List[WiFiNetwork]:
        """Get unique networks for export, removing any remaining duplicates"""
        seen_networks = set()
        unique_networks = []

        for network in self.discovered_networks:
            # Use SSID + BSSID as unique identifier
            identifier = f"{network.ssid}|{network.bssid or 'no_bssid'}"
            if identifier not in seen_networks:
                unique_networks.append(network)
                seen_networks.add(identifier)

        return unique_networks
    
    def show_statistics(self):
        """Show statistics"""
        if not self.discovered_networks:
            print("❌ No data to analyze")
            return

        open_networks = [n for n in self.discovered_networks if n.is_open]
        successful_attempts = [a for a in self.connection_attempts if a.success]

        if RICH_AVAILABLE:
            table = Table(title="📊 WiFi Scanner Statistics")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")

            table.add_row("Total scanned networks", str(len(self.discovered_networks)))
            table.add_row("Open networks", str(len(open_networks)))
            table.add_row("Connection attempts", str(len(self.connection_attempts)))
            table.add_row("Successful connections", str(len(successful_attempts)))

            if self.connection_attempts:
                success_rate = len(successful_attempts) / len(self.connection_attempts) * 100
                table.add_row("Success rate", f"{success_rate:.1f}%")

            self.console.print(table)
        else:
            print(f"📊 Statistics:")
            print(f"  • Total networks: {len(self.discovered_networks)}")
            print(f"  • Open networks: {len(open_networks)}")
            print(f"  • Connection attempts: {len(self.connection_attempts)}")
            print(f"  • Successful connections: {len(successful_attempts)}")

class WiFiScannerApp:
    """Main application with menu"""

    def __init__(self, show_banner=True):
        self.config = WiFiConfig()
        self.scanner = WiFiScanner(self.config)
        self.console = Console() if RICH_AVAILABLE else None
        if show_banner:
            self.show_banner()

    def show_banner(self):
        """Display ASCII art banner"""
        if RICH_AVAILABLE:
            banner = show_ascii_banner()
            self.console.print(f"[bold green]{banner}[/bold green]")
        else:
            banner = show_ascii_banner_simple()
            print(banner)

        # Add a small pause for dramatic effect
        time.sleep(1)

    def show_menu(self):
        """Show main menu"""
        if RICH_AVAILABLE:
            menu_text = """
[bold cyan]1.[/bold cyan] 📡 Continuous scanning
[bold cyan]2.[/bold cyan] 🔄 Auto-connect
[bold cyan]3.[/bold cyan] 🖥️  Scan network devices
[bold cyan]4.[/bold cyan] 📊 Show statistics
[bold cyan]5.[/bold cyan] 💾 Export to JSON
[bold cyan]6.[/bold cyan] ⚙️  Settings
[bold cyan]7.[/bold cyan] 📋 Log viewer
[bold cyan]q.[/bold cyan] ❌ Exit
"""
            panel = Panel(menu_text, title="🛜 WiFi Scanner Suite", border_style="blue")
            self.console.print(panel)
        else:
            print("\n" + "="*50)
            print("🛜  WiFi Scanner Suite")
            print("="*50)
            print("1. 📡 Continuous scanning")
            print("2. 🔄 Auto-connect")
            print("3. 🖥️  Scan network devices")
            print("4. 📊 Show statistics")
            print("5. 💾 Export to JSON")
            print("6. ⚙️  Settings")
            print("7. 📋 Log viewer")
            print("q. ❌ Exit")

    def scan_network_devices(self):
        """Scan and display network devices"""
        if RICH_AVAILABLE:
            self.console.print("\n[bold blue]🖥️  Scanning network devices...[/bold blue]")
        else:
            print("\n🖥️  Scanning network devices...")

        # Perform device scan
        devices = self.scanner.scan_network_devices()

        if not devices:
            if RICH_AVAILABLE:
                self.console.print("[yellow]⚠️  No devices found in network[/yellow]")
            else:
                print("⚠️  No devices found in network")
            return

        # Display results
        if RICH_AVAILABLE:
            self.console.print(f"\n[green]✅ Found {len(devices)} network devices[/green]")

            table = Table(title="🖥️  Network Devices")
            table.add_column("IP Address", style="cyan")
            table.add_column("MAC Address", style="magenta")
            table.add_column("Hostname", style="green")
            table.add_column("Vendor", style="yellow")

            for device in devices:
                table.add_row(
                    device.ip_address,
                    device.mac_address,
                    device.hostname or "-",
                    device.vendor or "-"
                )

            self.console.print(table)
        else:
            print(f"\n✅ Found {len(devices)} network devices")
            print("\n" + "="*80)
            print(f"{'IP Address':<15} {'MAC Address':<18} {'Hostname':<20} {'Vendor'}")
            print("-"*80)

            for device in devices:
                print(f"{device.ip_address:<15} {device.mac_address:<18} {device.hostname or '-':<20} {device.vendor or '-'}")

        input("\nPress Enter to continue...")

    def run(self):
        """Run main application loop"""
        if not self.scanner.check_dependencies():
            return

        while True:
            try:
                if RICH_AVAILABLE:
                    self.console.clear()

                self.show_menu()

                if RICH_AVAILABLE:
                    choice = Prompt.ask("\n[bold yellow]Select option[/bold yellow]", default="1")
                else:
                    choice = input("\nSelect option: ")

                if choice == "1":
                    self.scanner.continuous_scan()
                elif choice == "2":
                    self.scanner.auto_connect()
                elif choice == "3":
                    self.scan_network_devices()
                elif choice == "4":
                    self.scanner.show_statistics()
                elif choice == "5":
                    self.export_data()
                elif choice == "6":
                    self.show_settings()
                elif choice == "7":
                    self.show_logs()
                elif choice.lower() == "q":
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice")

                if choice != "1":  # Continuous scanning has its own pause
                    input("\nPress Enter to continue...")

            except KeyboardInterrupt:
                print("\n👋 Application terminated by user")
                break
    
    def export_data(self):
        """Export data to JSON file"""
        if not self.scanner.discovered_networks and not self.scanner.connection_attempts:
            print("❌ No data to export")
            return

        try:
            log_file = self.scanner.save_logs()
            print(f"✅ Data exported to: {log_file}")
        except Exception as e:
            print(f"❌ Export error: {e}")

    def show_settings(self):
        """Show settings"""
        print("\n⚙️  Current settings:")
        for key, value in self.config.config.items():
            print(f"  {key}: {value}")

    def show_logs(self):
        """Interactive log viewer"""
        self.log_viewer()

    def log_viewer(self):
        """Advanced interactive log viewer"""
        log_files = list(self.scanner.log_dir.glob("*.json"))
        if not log_files:
            print("❌ No log files found in directory")
            return

        # Sort files by modification time (newest first)
        log_files = sorted(log_files, key=lambda f: f.stat().st_mtime, reverse=True)

        while True:
            if RICH_AVAILABLE:
                self.console.clear()
                self.console.print("\n[bold cyan]📋 LOG VIEWER[/bold cyan]")
                self.console.print("="*50)
            else:
                print("\n" + "="*50)
                print("📋 LOG VIEWER")
                print("="*50)

            # Display available log files
            if RICH_AVAILABLE:
                table = Table(show_header=True, header_style="bold magenta")
                table.add_column("#", style="dim", width=3)
                table.add_column("Log File", style="cyan")
                table.add_column("Size", justify="right", style="green")
                table.add_column("Date", style="yellow")
                table.add_column("Networks", justify="right", style="blue")
                table.add_column("Attempts", justify="right", style="red")

                for i, log_file in enumerate(log_files, 1):
                    size = log_file.stat().st_size / 1024
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                    # Quick peek at file content for summary
                    networks_count = "?"
                    attempts_count = "?"
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            networks_count = str(len(data.get('networks', [])))
                            attempts_count = str(len(data.get('connection_attempts', [])))
                    except:
                        pass

                    table.add_row(
                        str(i),
                        log_file.name,
                        f"{size:.1f}KB",
                        mtime.strftime('%d.%m.%Y %H:%M'),
                        networks_count,
                        attempts_count
                    )

                self.console.print(table)
            else:
                print(f"\nAvailable log files ({len(log_files)}):")
                print("-" * 80)
                print(f"{'#':<3} {'File Name':<25} {'Size':<8} {'Date':<16} {'Networks':<8} {'Attempts'}")
                print("-" * 80)

                for i, log_file in enumerate(log_files, 1):
                    size = log_file.stat().st_size / 1024
                    mtime = datetime.fromtimestamp(log_file.stat().st_mtime)

                    # Quick peek at file content for summary
                    networks_count = "?"
                    attempts_count = "?"
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            networks_count = str(len(data.get('networks', [])))
                            attempts_count = str(len(data.get('connection_attempts', [])))
                    except:
                        pass

                    print(f"{i:<3} {log_file.name:<25} {size:>6.1f}KB {mtime.strftime('%d.%m.%Y %H:%M'):<16} {networks_count:<8} {attempts_count}")

            # User input
            if RICH_AVAILABLE:
                choice = Prompt.ask(
                    "\n[bold yellow]Select log number to view (or 'q' to quit)[/bold yellow]",
                    default="q"
                )
            else:
                choice = input(f"\nSelect log number (1-{len(log_files)}) or 'q' to quit: ").strip()

            if choice.lower() == 'q':
                break

            try:
                log_index = int(choice) - 1
                if 0 <= log_index < len(log_files):
                    self.display_log_content(log_files[log_index])
                else:
                    print("❌ Invalid log number")
                    input("Press Enter to continue...")
            except ValueError:
                print("❌ Please enter a valid number")
                input("Press Enter to continue...")

    def display_log_content(self, log_file: Path):
        """Display detailed content of selected log file"""
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"❌ Error reading log file: {e}")
            input("Press Enter to continue...")
            return

        while True:
            if RICH_AVAILABLE:
                self.console.clear()
                self.console.print(f"\n[bold green]📄 LOG: {log_file.name}[/bold green]")
                self.console.print("="*60)
            else:
                print("\n" + "="*60)
                print(f"📄 LOG: {log_file.name}")
                print("="*60)

            # Log summary
            timestamp = data.get('timestamp', 'Unknown')
            networks = data.get('networks', [])
            attempts = data.get('connection_attempts', [])
            devices = data.get('network_devices', [])

            if RICH_AVAILABLE:
                self.console.print(f"[bold]Timestamp:[/bold] {timestamp}")
                self.console.print(f"[bold]Networks found:[/bold] {len(networks)}")
                self.console.print(f"[bold]Connection attempts:[/bold] {len(attempts)}")
                self.console.print(f"[bold]Network devices:[/bold] {len(devices)}")
                self.console.print("\n[bold cyan]Options:[/bold cyan]")
                self.console.print("1. View all networks")
                self.console.print("2. View open networks only")
                self.console.print("3. View connection attempts")
                self.console.print("4. View network devices")
                self.console.print("5. View statistics")
                self.console.print("6. Back to log list")
            else:
                print(f"Timestamp: {timestamp}")
                print(f"Networks found: {len(networks)}")
                print(f"Connection attempts: {len(attempts)}")
                print(f"Network devices: {len(devices)}")
                print("\nOptions:")
                print("1. View all networks")
                print("2. View open networks only")
                print("3. View connection attempts")
                print("4. View network devices")
                print("5. View statistics")
                print("6. Back to log list")

            choice = input("\nSelect option: ").strip()

            if choice == "1":
                self.display_networks(networks, "All Networks")
            elif choice == "2":
                open_networks = [n for n in networks if not n.get('security', '')]
                self.display_networks(open_networks, "Open Networks")
            elif choice == "3":
                self.display_connection_attempts(attempts)
            elif choice == "4":
                self.display_network_devices(devices)
            elif choice == "5":
                self.display_log_statistics(networks, attempts)
            elif choice == "6":
                break
            else:
                print("❌ Invalid choice")
                input("Press Enter to continue...")

    def display_networks(self, networks: list, title: str):
        """Display networks in a formatted table"""
        if not networks:
            print(f"❌ No networks found in {title.lower()}")
            input("Press Enter to continue...")
            return

        if RICH_AVAILABLE:
            self.console.clear()
            self.console.print(f"\n[bold green]{title} ({len(networks)})[/bold green]")
            self.console.print("="*60)

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("SSID", style="cyan")
            table.add_column("Security", style="red")
            table.add_column("Signal", justify="right", style="green")
            table.add_column("Band", style="yellow")
            table.add_column("BSSID", style="dim")
            table.add_column("Channel", justify="right", style="blue")
            table.add_column("RSSI", justify="right", style="dim")

            for network in networks:
                security = network.get('security', '') or 'OPEN'
                signal = f"{network.get('signal', 0)}%"
                band = network.get('band', 'Unknown')
                bssid = network.get('bssid', 'N/A') or 'N/A'
                channel = str(network.get('channel', '?'))
                rssi = f"{network.get('rssi', '')}dBm" if network.get('rssi') else '-'

                # Color code open networks
                ssid_style = "green" if not network.get('security', '') else "white"

                table.add_row(
                    f"[{ssid_style}]{network.get('ssid', 'Unknown')}[/{ssid_style}]",
                    security,
                    signal,
                    band,
                    bssid,
                    channel,
                    rssi
                )

            self.console.print(table)
        else:
            print(f"\n{title} ({len(networks)})")
            print("="*100)
            print(f"{'SSID':<20} {'Security':<10} {'Signal':<8} {'Band':<8} {'BSSID':<18} {'Channel':<8} {'RSSI'}")
            print("-"*100)

            for network in networks:
                security = network.get('security', '') or 'OPEN'
                signal = f"{network.get('signal', 0)}%"
                band = network.get('band', 'Unknown')
                bssid = network.get('bssid', 'N/A') or 'N/A'
                channel = str(network.get('channel', '?'))
                rssi = f"{network.get('rssi', '')}dBm" if network.get('rssi') else '-'
                ssid = network.get('ssid', 'Unknown')

                # Mark open networks with green color
                if not network.get('security', ''):
                    ssid = f"\033[92m{ssid}\033[0m"

                print(f"{ssid:<20} {security:<10} {signal:<8} {band:<8} {bssid:<18} {channel:<8} {rssi}")

        input("\nPress Enter to continue...")

    def display_connection_attempts(self, attempts: list):
        """Display connection attempts"""
        if not attempts:
            print("❌ No connection attempts found")
            input("Press Enter to continue...")
            return

        if RICH_AVAILABLE:
            self.console.clear()
            self.console.print(f"\n[bold green]Connection Attempts ({len(attempts)})[/bold green]")
            self.console.print("="*60)

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("SSID", style="cyan")
            table.add_column("Result", style="white")
            table.add_column("IP Address", style="green")
            table.add_column("Signal", justify="right", style="yellow")
            table.add_column("Ping", style="blue")
            table.add_column("Time", style="dim")

            for attempt in attempts:
                result = "✅ Success" if attempt.get('success') else "❌ Failed"
                result_style = "green" if attempt.get('success') else "red"
                ip_addr = attempt.get('ip_address', '-')
                signal = f"{attempt.get('signal', 0)}%"
                ping_info = attempt.get('ping_stats', 'No ping' if not attempt.get('ping_success') else 'Success')
                timestamp = attempt.get('timestamp', '')
                try:
                    time_str = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%H:%M:%S')
                except:
                    time_str = timestamp[:8] if len(timestamp) > 8 else timestamp

                table.add_row(
                    attempt.get('ssid', 'Unknown'),
                    f"[{result_style}]{result}[/{result_style}]",
                    ip_addr,
                    signal,
                    ping_info,
                    time_str
                )

            self.console.print(table)
        else:
            print(f"\nConnection Attempts ({len(attempts)})")
            print("="*80)
            print(f"{'SSID':<15} {'Result':<10} {'IP Address':<15} {'Signal':<8} {'Ping':<20} {'Time'}")
            print("-"*80)

            for attempt in attempts:
                result = "✅ Success" if attempt.get('success') else "❌ Failed"
                ip_addr = attempt.get('ip_address', '-')
                signal = f"{attempt.get('signal', 0)}%"
                ping_info = attempt.get('ping_stats', 'No ping' if not attempt.get('ping_success') else 'Success')
                timestamp = attempt.get('timestamp', '')
                try:
                    time_str = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).strftime('%H:%M:%S')
                except:
                    time_str = timestamp[:8] if len(timestamp) > 8 else timestamp

                print(f"{attempt.get('ssid', 'Unknown'):<15} {result:<10} {ip_addr:<15} {signal:<8} {ping_info:<20} {time_str}")

        input("\nPress Enter to continue...")

    def display_network_devices(self, devices: List[dict]):
        """Display network devices from log"""
        if not devices:
            if RICH_AVAILABLE:
                self.console.print("[yellow]⚠️  No network devices in this log[/yellow]")
            else:
                print("⚠️  No network devices in this log")
            input("\nPress Enter to continue...")
            return

        title = f"Network Devices ({len(devices)})"

        if RICH_AVAILABLE:
            table = Table(title=f"🖥️  {title}")
            table.add_column("IP Address", style="cyan")
            table.add_column("MAC Address", style="magenta")
            table.add_column("Hostname", style="green")
            table.add_column("Vendor", style="yellow")
            table.add_column("Timestamp", style="dim")

            for device in devices:
                timestamp = device.get('timestamp', '')
                if timestamp:
                    # Format timestamp for display
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.strftime('%H:%M:%S')
                    except:
                        timestamp = timestamp[:8] if len(timestamp) > 8 else timestamp

                table.add_row(
                    device.get('ip_address', 'Unknown'),
                    device.get('mac_address', 'Unknown'),
                    device.get('hostname', '-') or '-',
                    device.get('vendor', '-') or '-',
                    timestamp
                )

            self.console.print(table)
        else:
            print(f"\n{title}")
            print("="*90)
            print(f"{'IP Address':<15} {'MAC Address':<18} {'Hostname':<20} {'Vendor':<25} {'Time'}")
            print("-"*90)

            for device in devices:
                timestamp = device.get('timestamp', '')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.strftime('%H:%M:%S')
                    except:
                        timestamp = timestamp[:8] if len(timestamp) > 8 else timestamp

                ip = device.get('ip_address', 'Unknown')
                mac = device.get('mac_address', 'Unknown')
                hostname = device.get('hostname', '-') or '-'
                vendor = device.get('vendor', '-') or '-'

                print(f"{ip:<15} {mac:<18} {hostname:<20} {vendor:<25} {timestamp}")

        input("\nPress Enter to continue...")

    def display_log_statistics(self, networks: list, attempts: list):
        """Display statistics from log data"""
        if RICH_AVAILABLE:
            self.console.clear()
            self.console.print("\n[bold green]📊 LOG STATISTICS[/bold green]")
            self.console.print("="*50)
        else:
            print("\n" + "="*50)
            print("📊 LOG STATISTICS")
            print("="*50)

        # Network statistics
        open_networks = [n for n in networks if not n.get('security', '')]
        secured_networks = [n for n in networks if n.get('security', '')]

        # Band statistics
        band_24 = [n for n in networks if n.get('band') == '2.4GHz']
        band_5 = [n for n in networks if n.get('band') == '5GHz']
        band_6 = [n for n in networks if n.get('band') == '6GHz']

        # Connection statistics
        successful_attempts = [a for a in attempts if a.get('success')]
        failed_attempts = [a for a in attempts if not a.get('success')]

        if RICH_AVAILABLE:
            # Networks panel
            networks_info = f"""
[bold]Total Networks:[/bold] {len(networks)}
[green]• Open Networks:[/green] {len(open_networks)}
[red]• Secured Networks:[/red] {len(secured_networks)}

[bold]By Frequency Band:[/bold]
[yellow]• 2.4GHz:[/yellow] {len(band_24)}
[cyan]• 5GHz:[/cyan] {len(band_5)}
[magenta]• 6GHz:[/magenta] {len(band_6)}
            """

            attempts_info = f"""
[bold]Connection Attempts:[/bold] {len(attempts)}
[green]• Successful:[/green] {len(successful_attempts)}
[red]• Failed:[/red] {len(failed_attempts)}
            """

            self.console.print(Panel(networks_info.strip(), title="Networks", border_style="blue"))
            self.console.print(Panel(attempts_info.strip(), title="Connections", border_style="green"))
        else:
            print(f"\nNetworks:")
            print(f"  Total Networks: {len(networks)}")
            print(f"  • Open Networks: {len(open_networks)}")
            print(f"  • Secured Networks: {len(secured_networks)}")
            print(f"\nBy Frequency Band:")
            print(f"  • 2.4GHz: {len(band_24)}")
            print(f"  • 5GHz: {len(band_5)}")
            print(f"  • 6GHz: {len(band_6)}")
            print(f"\nConnection Attempts:")
            print(f"  Total Attempts: {len(attempts)}")
            print(f"  • Successful: {len(successful_attempts)}")
            print(f"  • Failed: {len(failed_attempts)}")

        input("\nPress Enter to continue...")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="WiFi Scanner Suite")
    parser.add_argument("--scan", action="store_true", help="One-time scanning")
    parser.add_argument("--auto", action="store_true", help="Auto-connect")
    parser.add_argument("--continuous", action="store_true", help="Continuous scanning")
    parser.add_argument("--no-banner", action="store_true", help="Skip ASCII banner")

    args = parser.parse_args()

    # Show banner unless explicitly disabled
    if not args.no_banner:
        if RICH_AVAILABLE:
            console = Console()
            banner = show_ascii_banner()
            console.print(f"[bold green]{banner}[/bold green]")
        else:
            banner = show_ascii_banner_simple()
            print(banner)
        time.sleep(1)

    # Create app without banner if we already showed it or if disabled
    app = WiFiScannerApp(show_banner=False)

    if args.scan:
        networks = app.scanner.scan_networks()
        print(f"Found {len(networks)} networks")
    elif args.auto:
        app.scanner.auto_connect()
    elif args.continuous:
        app.scanner.continuous_scan()
    else:
        app.run()

if __name__ == "__main__":
    main()