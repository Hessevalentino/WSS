#!/usr/bin/env python3
"""
WSS - WiFi Scanner Suite
Author: OK2HSS
Version: 2.0

Features:
- Continuous WiFi scanning
- Auto-connect to open networks
- Advanced log viewer
- Export to JSON/CSV
- Interactive menu
"""

import subprocess
import json
import csv
import time
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
            if not line or line.count(':') < 5:
                continue

            parts = line.split(':')
            ssid = parts[0].strip()
            security = parts[1].strip()

            if not ssid:  # Skip empty SSID
                continue

            try:
                signal = int(parts[2]) if parts[2].isdigit() else 0
                freq_str = parts[3].strip()
                bssid = parts[4] if len(parts) > 4 else ""
                channel_str = parts[5] if len(parts) > 5 else ""

                # Parse frequency - nmcli returns frequency in MHz
                freq = 0
                if freq_str:
                    # Try different formats: "2412", "2412 MHz", "2.412 GHz"
                    freq_clean = freq_str.replace('MHz', '').replace('GHz', '').replace(' ', '').strip()
                    try:
                        if '.' in freq_clean:
                            # Handle "2.412" format (GHz) - convert to MHz
                            freq = int(float(freq_clean) * 1000)
                        else:
                            # Handle "2412" format (MHz)
                            freq = int(freq_clean)
                    except ValueError:
                        freq = 0

                # Parse channel
                channel = None
                if channel_str and channel_str.isdigit():
                    channel = int(channel_str)

                # Get RSSI if available
                rssi = rssi_data.get(ssid, None)

                network = WiFiNetwork(
                    ssid=ssid,
                    security=security,
                    signal=signal,
                    frequency=freq,
                    band="Unknown",  # Will be determined in __post_init__
                    channel=channel,
                    bssid=bssid,
                    rssi=rssi
                )
                networks.append(network)

            except (ValueError, IndexError):
                continue

        # Save to discovered networks list
        self.discovered_networks.extend(networks)
        return networks
    
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
                        print(f"  → \033[92m{net.ssid}\033[0m ({net.signal}%{rssi_display} {band_display}) \033[92m[OPEN]\033[0m")

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

                    table.add_row(
                        ssid_display,
                        security_display,
                        signal_display,
                        band_display,
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

    def save_logs(self, format_type: str = "json"):
        """Save logs to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format_type == "json":
            log_file = self.log_dir / f"wifi_scan_{timestamp}.json"
            data = {
                "timestamp": datetime.now().isoformat(),
                "networks": [asdict(n) for n in self.discovered_networks],
                "connection_attempts": [asdict(a) for a in self.connection_attempts]
            }

            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        elif format_type == "csv":
            # CSV for networks
            networks_file = self.log_dir / f"wifi_networks_{timestamp}.csv"
            if self.discovered_networks:
                with open(networks_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=asdict(self.discovered_networks[0]).keys())
                    writer.writeheader()
                    for network in self.discovered_networks:
                        writer.writerow(asdict(network))

            # CSV for connection attempts
            attempts_file = self.log_dir / f"wifi_attempts_{timestamp}.csv"
            if self.connection_attempts:
                with open(attempts_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=asdict(self.connection_attempts[0]).keys())
                    writer.writeheader()
                    for attempt in self.connection_attempts:
                        writer.writerow(asdict(attempt))

            # Return the networks file for CSV format
            log_file = networks_file

        return log_file
    
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
[bold cyan]3.[/bold cyan] 📊 Show statistics
[bold cyan]4.[/bold cyan] 💾 Export data
[bold cyan]5.[/bold cyan] ⚙️  Settings
[bold cyan]6.[/bold cyan] 📋 Show logs
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
            print("3. 📊 Show statistics")
            print("4. 💾 Export data")
            print("5. ⚙️  Settings")
            print("6. 📋 Show logs")
            print("q. ❌ Exit")
    
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
                    self.scanner.show_statistics()
                elif choice == "4":
                    self.export_data()
                elif choice == "5":
                    self.show_settings()
                elif choice == "6":
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
        """Export data"""
        if not self.scanner.discovered_networks and not self.scanner.connection_attempts:
            print("❌ No data to export")
            return

        if RICH_AVAILABLE:
            format_choice = Prompt.ask(
                "Select format",
                choices=["json", "csv"],
                default="json"
            )
        else:
            format_choice = input("Format (json/csv): ").lower() or "json"

        try:
            log_file = self.scanner.save_logs(format_choice)
            print(f"✅ Data exported to: {log_file}")
        except Exception as e:
            print(f"❌ Export error: {e}")

    def show_settings(self):
        """Show settings"""
        print("\n⚙️  Current settings:")
        for key, value in self.config.config.items():
            print(f"  {key}: {value}")

    def show_logs(self):
        """Show available logs"""
        log_files = list(self.scanner.log_dir.glob("*.json"))
        if not log_files:
            print("❌ No logs found")
            return

        print(f"\n📋 Available logs ({len(log_files)}):")
        for log_file in sorted(log_files, reverse=True)[:10]:
            size = log_file.stat().st_size / 1024
            mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
            print(f"  • {log_file.name} ({size:.1f}KB, {mtime.strftime('%d.%m.%Y %H:%M')})")

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