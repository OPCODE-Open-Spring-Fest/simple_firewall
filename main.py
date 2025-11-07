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
import threading
import time


ASCII_ART=r"""
     _                 _         __ _                        _ _ 
    (_)               | |       / _(_)                      | | |
 ___ _ _ __ ___  _ __ | | ___  | |_ _ _ __ _____      ____ _| | |
/ __| | '_ ` _ \| '_ \| |/ _ \ |  _| | '__/ _ \ \ /\ / / _` | | |
\__ \ | | | | | | |_) | |  __/ | | | | | |  __/\ V  V / (_| | | |
|___/_|_| |_| |_| .__/|_|\___| |_| |_|_|  \___| \_/\_/ \__,_|_|_|
                | |                                              
                |_|                                              
"""

# Add src directory to Python path for absolute imports
current_dir = Path(__file__).parent
src_dir = current_dir / 'src'
sys.path.insert(0, str(src_dir))
_SHUTDOWN_INITIATED = False
_SHUTDOWN_LOCK = threading.Lock()

try:
    from firewall.core import SimpleFirewall
    from utils.system import get_system_info, format_bytes
    from colorama import Fore, Style, init
    import psutil
except ImportError as e:
    print(f"Required package missing: {e}")
    print("Run: pip install -r requirements.txt")
    sys.exit(1)

# Initialize colorama
init(autoreset=True)


def show_system_stats():
    """Show system network statistics"""
    print(f"{Fore.CYAN}=== System Network Statistics ==={Style.RESET_ALL}")
    
    try:
        import psutil
        
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
            if not interface.startswith(('lo', 'docker', 'veth')):
                print(f"{interface}:")
                for addr in addresses:
                    if addr.family.name in ['AF_INET', 'AF_INET6']:
                        print(f"  {addr.family.name}: {addr.address}")
        
    except Exception as e:
        print(f"Error getting stats: {e}")

def get_available_interfaces():
    """Get a list of non-loopback/docker network interfaces."""
    interfaces = []
    try:
        addrs = psutil.net_if_addrs()
        for interface, addresses in addrs.items():
            if not interface.startswith(('lo', 'docker', 'veth', 'br-')):
                interfaces.append(interface)
    except Exception as e:
        print(f"{Fore.RED}Error getting interfaces: {e}{Style.RESET_ALL}")
    return interfaces

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
        %(prog)s                       # Start interactively
        %(prog)s -i eth0               # Monitor specific interface
        %(prog)s -c custom_config.json # Use custom config file
        %(prog)s --stats               # Show system statistics
        %(prog)s --create-config       # Create sample config file
                """
    )
    
    parser.add_argument('-i', '--interface', 
                        help='Network interface to monitor (auto-detected if not specified)')
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
    
    # Handle special commands
    if args.stats:
        show_system_stats()
        return
    
    if args.create_config:
        create_sample_config()
        return

    selected_interface = None

    if args.interface:
        selected_interface = args.interface
    else:
        
        print(f"{Fore.GREEN}{ASCII_ART}{Style.RESET_ALL}") 
        separator = "-" * 25
        print(separator)
        try:
            sys_info = get_system_info()
            print(f"OS detected: {sys_info['platform']}")
        except Exception:
            print(f"{Fore.YELLOW}Could not detect OS.{Style.RESET_ALL}")
        
        print(separator)
        interfaces = get_available_interfaces()
        if not interfaces:
            print(f"{Fore.RED}No suitable network interfaces found.{Style.RESET_ALL}")
            sys.exit(1)
            
        print("\nAvailable network interfaces:")
        print("[0] Exit")
        for i, iface in enumerate(interfaces, 1):
            print(f"[{i}] {iface}")
        while True:
            try:
                choice_str = input(f"\nSelect an interface (0-{len(interfaces)}): ")
                choice = int(choice_str)
                
                if choice == 0:
                    print("Exiting.")
                    sys.exit(0)
                elif 1 <= choice <= len(interfaces):
                    selected_interface = interfaces[choice - 1]
                    break
                else:
                    print(f"{Fore.YELLOW}Invalid choice. Please enter a number between 0 and {len(interfaces)}.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.YELLOW}Invalid input. Please enter a number.{Style.RESET_ALL}")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                sys.exit(0)
    try:
        # Use the interface chosen either by argument or menu
        firewall = SimpleFirewall(
            interface=selected_interface, 
            config_file=args.config
        )
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            """Enhanced signal handler with timeout and state tracking"""
            global _SHUTDOWN_INITIATED
            
            with _SHUTDOWN_LOCK:
                if _SHUTDOWN_INITIATED:
                    print(f"\n{Fore.RED}Forced shutdown initiated...{Style.RESET_ALL}")
                    os._exit(1)
                    
                _SHUTDOWN_INITIATED = True
            
            print(f"\n{Fore.YELLOW}Signal {signum} received, initiating graceful shutdown...{Style.RESET_ALL}")
            
            def force_shutdown():
                time.sleep(5)
                print(f"\n{Fore.RED}Graceful shutdown timeout, forcing exit...{Style.RESET_ALL}")
                os._exit(1)
            
            force_thread = threading.Thread(target=force_shutdown, daemon=True)
            force_thread.start()
            
            try:
                if 'firewall' in locals():
                    firewall.stop()
                print(f"{Fore.GREEN}Firewall shutdown completed successfully.{Style.RESET_ALL}")
                sys.exit(0)
            except Exception as e:
                print(f"{Fore.RED}Error during shutdown: {e}{Style.RESET_ALL}")
                os._exit(1)
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        print(f"{Fore.CYAN}Starting firewall on interface: {selected_interface}{Style.RESET_ALL}")
        firewall.start()

        # Keep main thread alive
        while firewall.is_running():
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Interrupted by user{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}Fatal error: {e}{Style.RESET_ALL}")
        if args.verbose:
            print(f"\n{Fore.RED}Traceback:{Style.RESET_ALL}")
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()