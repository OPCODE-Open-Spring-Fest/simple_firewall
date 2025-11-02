"""Main firewall orchestration and coordination"""

import threading
import time
import signal
import sys
from scapy.all import sniff,AsyncSniffer
from colorama import Fore, Style
from typing import Optional

from config.loader import ConfigLoader
from network.interface import NetworkInterface
from network.packet_handler import PacketHandler
from firewall.detection import AttackDetector
from firewall.blocking import IPBlocker
from firewall.stats import FirewallStats
from utils.logger import setup_logging, get_logger
from utils.system import check_root_privileges


class SimpleFirewall:
    """Main firewall class that orchestrates all components"""
    
    def __init__(self, interface: str = None, config_file: str = None):
        # Load configuration
        config_loader = ConfigLoader(config_file)
        self.config = config_loader.load_config()
        
        # Setup logging
        self.logger = setup_logging(self.config.log_level)
        
        # Initialize components
        self.network = NetworkInterface(interface)
        self.detector = AttackDetector(self.config.thresholds, set(self.config.whitelist))
        self.blocker = IPBlocker(self.config.block_duration, set(self.config.whitelist))
        self.stats = FirewallStats()
        
        # Create packet handler with our callback
        self.packet_handler = PacketHandler(self._process_packet)
        
        # Control flags
        self.running = False
        self._threads = []

        self._sniffer = None
        self._stop_event = threading.Event()
        
        self.logger.info("Simple Firewall initialized successfully")
    
    def _process_packet(self, packet) -> None:
        """Process a single packet for potential attacks"""
        try:
            # Update statistics
            packet_size = len(packet) if hasattr(packet, '__len__') else 0
            self.stats.record_packet(packet_size)
            
            # Detect attacks
            attack_result = self.detector.detect_attacks(packet)
            
            if attack_result:
                ip, reason = attack_result
                
                # Block the IP
                if self.blocker.block_ip(ip, reason):
                    self.stats.record_attack(reason, ip)
                    
        except Exception as e:
            self.logger.error(f"Error processing packet: {e}")
    
    def _cleanup_thread(self):
        """Background thread to clean up expired blocks"""
        self.logger.info("Cleanup thread started")
        
        while self.running:
            try:
                unblocked_ips = self.blocker.unblock_expired_ips()
                if unblocked_ips:
                    self.logger.info(f"Unblocked expired IPs: {unblocked_ips}")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in cleanup thread: {e}")
                time.sleep(30)
    
    def _stats_thread(self):
        """Background thread to display statistics"""
        self.logger.info("Statistics thread started")
        
        while self.running:
            try:
                time.sleep(60)  # Update every minute
                if self.running:  # Check again after sleep
                    self._display_stats()
                    
            except Exception as e:
                self.logger.error(f"Error in stats thread: {e}")
                time.sleep(60)
    
    def _display_stats(self):
        """Display current firewall statistics"""
        stats_summary = self.stats.get_summary()
        blocker_stats = self.blocker.get_stats()
        detection_stats = self.detector.get_detection_stats()
        
        print(f"\n{Fore.CYAN}=== Firewall Statistics ==={Style.RESET_ALL}")
        print(f"Uptime: {stats_summary['uptime']}")
        print(f"Packets analyzed: {stats_summary['packets_analyzed']:,}")
        print(f"Data processed: {stats_summary['bytes_analyzed']}")
        print(f"Packets/sec: {self.stats.get_packets_per_second():.2f}")
        print(f"Currently blocked IPs: {blocker_stats['currently_blocked']}")
        print(f"Total attacks blocked: {stats_summary['total_attacks_blocked']}")
        
        if stats_summary['attack_types']:
            print(f"\n{Fore.YELLOW}Attack Types Detected:{Style.RESET_ALL}")
            for attack_type, count in stats_summary['attack_types'].items():
                print(f"  {attack_type}: {count}")
        
        # Show interface info
        interface_info = self.network.get_interface_info()
        print(f"\n{Fore.BLUE}Network Interface: {interface_info['name']}{Style.RESET_ALL}")
        if interface_info.get('ipv4'):
            for addr in interface_info['ipv4'][:2]:  # Show first 2 addresses
                print(f"  IPv4: {addr['addr']}")
    
    def start(self):
        """Start the firewall"""
        # Check privileges
        if not check_root_privileges():
            print(f"{Fore.RED}This script requires root/administrator privileges.{Style.RESET_ALL}")
            print(f"Please run with elevated privileges (sudo on Unix, 'Run as Administrator' on Windows)")
            sys.exit(1)
        
        self.running = True
        
        print(f"{Fore.GREEN}🛡️  Starting Simple Firewall{Style.RESET_ALL}")
        print(f"Interface: {self.network.interface}")
        print(f"Block duration: {self.config.block_duration} seconds")
        print(f"Whitelist: {len(self.config.whitelist)} IPs")
        print(f"Platform: {self.blocker.platform}")
        print(f"Monitoring for DDoS/DoS attacks...")
        print(f"Press Ctrl+C to stop\n")
        
        # Start background threads
        cleanup_thread = threading.Thread(target=self._cleanup_thread, daemon=True)
        stats_thread = threading.Thread(target=self._stats_thread, daemon=True)
        
        cleanup_thread.start()
        stats_thread.start()
        
        self._threads = [cleanup_thread, stats_thread]
        
        try:
            # Start packet capture
            self.logger.info(f"Starting packet capture on interface: {self.network.interface}")
            sniff(
                iface=self.network.interface,
                prn=self.packet_handler.handle_packet,
                store=False,
                stop_filter=lambda x: not self.running
            )
            
        except PermissionError:
            print(f"{Fore.RED}Error: Permission denied. Run with elevated privileges.{Style.RESET_ALL}")
            sys.exit(1)
        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            self.logger.error(f"Error in packet capture: {e}")
            self.stop()
    
    def stop(self):
        """Stop the firewall and cleanup - ENHANCED VERSION"""
        if not self.running:
            return
            
        print(f"\n{Fore.YELLOW}Stopping firewall...{Style.RESET_ALL}")
        self.running = False
        self._stop_event.set()
        
        if self._sniffer and self._sniffer.running:
            self._sniffer.stop()
        
        timeout = 3.0
        start_time = time.time()
        
        for thread in self._threads:
            if thread.is_alive():
                remaining_time = timeout - (time.time() - start_time)
                if remaining_time > 0:
                    thread.join(timeout=remaining_time)
        
        cleaned_ips = self.blocker.cleanup_all_blocks()
        if cleaned_ips:
            self.logger.info(f"Cleaned up blocks for {len(cleaned_ips)} IPs")
        
        self._display_stats()
        print(f"{Fore.GREEN}Firewall stopped successfully.{Style.RESET_ALL}")
    
    def get_status(self) -> dict:
        """Get current firewall status"""
        return {
            'running': self.running,
            'interface': self.network.interface,
            'config': {
                'block_duration': self.config.block_duration,
                'whitelist_size': len(self.config.whitelist),
                'thresholds': {
                    'syn_flood': self.config.thresholds.syn_flood_threshold,
                    'connection': self.config.thresholds.connection_threshold,
                    'packet_rate': self.config.thresholds.packet_rate_threshold,
                    'port_scan': self.config.thresholds.port_scan_threshold,
                    'icmp_flood': self.config.thresholds.icmp_flood_threshold
                }
            },
            'stats': self.stats.get_summary(),
            'blocked_ips': self.blocker.get_blocked_ips()
        }