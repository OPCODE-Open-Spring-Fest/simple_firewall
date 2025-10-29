#!/usr/bin/env python3
"""
Simple Firewall - Main Entry Point
A lightweight firewall that monitors network traffic and blocks potential DDoS/DoS attacks
"""

import sys
import os
import argparse
import signal
import traceback
from pathlib import Path

# Add src directory to Python path for absolute imports
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))

try:
    from firewall.core import SimpleFirewall
    from utils.system import get_system_info, format_bytes
    from network.interface import list_interfaces # Import function to list network interfaces
    from colorama import Fore, Style, init
    import psutil
except ImportError as e:
    print(f"Required package missing: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Initialize colorama
init(autoreset=True)

# --- ASCII Art Banner ---
FIREWALL_BANNER = f"""
{Fore.LIGHTMAGENTA}
  _____ _                 _       __        __
 |  ___(_)               | |      \ \      / /
 | |__  _ _ __ ___  _   _| | ___   \ \    / / 
 |  __|| | '_ ` _ \| | | | |/ _ \   > \  / <  
 | |___| | | | | | | |_| | |  __/  / /\ \  /\ \\
 \____/|_|_| |_| |_|\__, |_|\___| /_/  \_\/_/  
                     __/ |                  
                    |___/                   
{Style.RESET_ALL}
Simple DDoS/DoS Protection Firewall
"""

def display_banner():
    """Displays the ASCII art banner."""
    print(FIREWALL_BANNER)

def show_system_stats():
    """Show system network statistics"""
    print(f"{Fore.CYAN}=== System Network Statistics ==={Style.RESET_ALL}")
    
    try:
        # Network stats
        net_stats = psutil.net_io_counters()
        print(f"Bytes sent: {format_bytes(net_stats.bytes_sent)}")
        print(f"Bytes received: {format_bytes(net_stats.bytes_recv)}")
        print(f"Packets sent: {net_stats.packets_sent:,}")
        print(f"Packets received: {net_stats.packets_recv:,}")
        
        # System info
        sys_info = get_system_info()
        print(f"\n{Fore.BLUE}=== System Information ==={Style.RESET_ALL}")
        print(f"Platform: {sys_info['platform']} {sys_info['architecture']}")
        print(f"Python: {sys_info['python_version']}")
        print(f"CPU cores: {sys_info['cpu_count']}")
        print(f"Memory: {format_bytes(sys_info['memory_total'])}")
        print(f"Disk usage: {sys_info['disk_usage']:.1f}%")
        
        # Network interfaces
        addrs = psutil.net_if_addrs()
        print(f"\n{Fore.GREEN}=== Network Interfaces ==={Style.RESET_ALL}")
        for interface, addresses in addrs.items():
            # Filter out loopback, docker, virtual, and bridge interfaces by default
            if not interface.startswith(('lo', 'docker', 'veth', 'br-')):
                print(f"{interface}:")
                for addr in addresses:
                    if addr.family.name in ['AF_INET', 'AF_INET6']:
                        print(f"  {addr.family.name}: {addr.address}")
        
    except Exception as e:
        print(f"Error getting stats: {e}")


def create_sample_config():
    """Create a sample configuration file"""
    config_path = current_dir / 'firewall_config.json'
    
    if config_path.exists():
        print(f"{Fore.YELLOW}Configuration file already exists at {config_path}{Style.RESET_ALL}")
        return
    
    sample_config = """{
    "thresholds": {
        "syn_flood_threshold": 1000,
        "connection_threshold": 200,
        "packet_rate_threshold": 1000,
        "port_scan_threshold": 80,
        "icmp_flood_threshold": 1000
    },
    "whitelist": [
        "::1",
        "127.0.0.1",
        "192.168.1.0/24"
    ],
    "block_duration": 300,
    "log_level": "INFO"
}"""
    
    try:
        with open(config_path, 'w') as f:
            f.write(sample_config)
        print(f"{Fore.GREEN}Sample configuration created at {config_path}{Style.RESET_ALL}")
        print(f"Edit this file to customize your firewall settings.")
    except Exception as e:
        print(f"{Fore.RED}Error creating config file: {e}{Style.RESET_ALL}")


def main():
    """Main entry point for the firewall application"""
    parser = argparse.ArgumentParser(
        description='Simple DDoS/DoS Protection Firewall',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start with interactive interface selection
  %(prog)s -i eth0                  # Monitor specific interface (overrides interactive selection)
  %(prog)s -c custom_config.json    # Use custom config file
  %(prog)s --stats                  # Show system statistics
  %(prog)s --create-config          # Create sample config file
        """
    )
    
    parser.add_argument('-i', '--interface', 
                       help='Network interface to monitor (interactive selection if not specified)')
    parser.add_argument('-c', '--config', 
                       help='Configuration file path (default: firewall_config.json)')
    parser.add_argument('--stats', action='store_true', 
                       help='Show system network statistics and exit')
    parser.add_argument('--create-config', action='store_true',
                       help='Create sample configuration file and exit')
    parser.add_argument('--version', action='version', version='Simple Firewall 1.0.0')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Handle special commands (stats, create-config) which should exit early
    if args.stats:
        show_system_stats()
        return
    
    if args.create_config:
        create_sample_config()
        return

    # Display banner for normal operation (not for stats or config creation)
    display_banner()
    
    selected_interface = None

    # Determine the network interface to monitor
    if args.interface:
        # If interface is specified via command-line argument, use it directly
        selected_interface = args.interface
        print(f"{Fore.CYAN}Monitoring interface specified via --interface: {selected_interface}{Style.RESET_ALL}")
    else:
        # Otherwise, engage interactive selection
        available_interfaces = list_interfaces()
        
        if not available_interfaces:
            print(f"{Fore.RED}No active network interfaces found. Cannot proceed.{Style.RESET_ALL}")
            sys.exit(1)
        
        print(f"\n{Fore.GREEN}Select a network interface to monitor:{Style.RESET_ALL}")
        for i, iface in enumerate(available_interfaces):
            print(f"  {i+1}. {iface}")
        print(f"  {Fore.YELLOW}0. Exit{Style.RESET_ALL}")
        
        while selected_interface is None:
            try:
                choice = input(f"{Fore.CYAN}Enter your choice (0-{len(available_interfaces)}): {Style.RESET_ALL}").strip()
                choice_int = int(choice)
                
                if choice_int == 0:
                    print(f"{Fore.YELLOW}Exiting program.{Style.RESET_ALL}")
                    sys.exit(0)
                elif 1 <= choice_int <= len(available_interfaces):
                    selected_interface = available_interfaces[choice_int - 1]
                    print(f"{Fore.GREEN}Selected interface: {selected_interface}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Invalid choice. Please enter a number between 0 and {len(available_interfaces)}.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                print(f"\n{Fore.YELLOW}Interrupted during selection, exiting.{Style.RESET_ALL}")
                sys.exit(0)

    # Proceed only if an interface has been successfully selected
    if selected_interface:
        try:
            firewall = SimpleFirewall(
                interface=selected_interface, 
                config_file=args.config
            )
            
            # Setup signal handlers for graceful shutdown
            def signal_handler(signum, frame):
                print(f"\n{Fore.YELLOW}Signal {signum} received, shutting down...{Style.RESET_ALL}")
                firewall.stop()
                sys.exit(0)
            
            signal.signal(signal.SIGINT, signal_handler)
            signal.signal(signal.SIGTERM, signal_handler)
            
            # Start the firewall
            firewall.start()
            
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
            sys.exit(0)
        except Exception as e:
            print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
            if args.verbose:
                print(f"\n{Fore.RED}Traceback:{Style.RESET_ALL}")
                traceback.print_exc()
            sys.exit(1)
    else:
        # This branch should theoretically not be reached if previous logic is sound
        print(f"{Fore.RED}No network interface was selected. Exiting.{Style.RESET_ALL}")
        sys.exit(1)


if __name__ == "__main__":
    main()