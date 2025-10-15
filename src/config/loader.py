"""Configuration loading and validation"""

import os
import sys
import json
from typing import Dict
from colorama import Fore, Style
from config.models import FirewallConfig


class ConfigLoader:
    """Handles configuration file loading and validation"""
    
    def __init__(self, config_file: str = None):
        self.config_file = config_file or 'firewall_config.json'
    
    def load_config(self) -> FirewallConfig:
        """Load configuration from file - config file is required"""
        config_path = self.config_file
        
        if not os.path.exists(config_path):
            self._show_config_template(config_path)
            sys.exit(1)
        
        try:
            with open(config_path, 'r') as f:
                config_dict = json.load(f)
            
            # Validate required sections
            if 'thresholds' not in config_dict:
                print(f"{Fore.RED}Error: 'thresholds' section missing in {config_path}{Style.RESET_ALL}")
                self._show_config_template(config_path)
                sys.exit(1)
                
            required_thresholds = [
                'syn_flood_threshold', 'connection_threshold', 'packet_rate_threshold',
                'port_scan_threshold', 'icmp_flood_threshold'
            ]
            
            missing_thresholds = [t for t in required_thresholds if t not in config_dict['thresholds']]
            if missing_thresholds:
                print(f"{Fore.RED}Error: Missing threshold values in {config_path}:{Style.RESET_ALL}")
                for threshold in missing_thresholds:
                    print(f"  - {threshold}")
                self._show_config_template(config_path)
                sys.exit(1)
            
            return FirewallConfig.from_dict(config_dict)
            
        except json.JSONDecodeError as e:
            print(f"{Fore.RED}Error: Invalid JSON in {config_path}: {e}{Style.RESET_ALL}")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}Error loading config {config_path}: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def _show_config_template(self, config_path: str):
        """Show configuration file template"""
        template = {
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
        }
        
        print(f"{Fore.YELLOW}Configuration file '{config_path}' not found or incomplete.{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Please create {config_path} with the following template:{Style.RESET_ALL}\n")
        print(json.dumps(template, indent=4))
        print(f"\n{Fore.GREEN}Configuration options explained:{Style.RESET_ALL}")
        print("• syn_flood_threshold: Max SYN packets per IP per minute")
        print("• connection_threshold: Max connections per IP per minute") 
        print("• packet_rate_threshold: Max total packets per IP per minute")
        print("• port_scan_threshold: Max different ports accessed per IP per minute")
        print("• icmp_flood_threshold: Max ICMP packets per IP per minute")
        print("• whitelist: IP addresses/ranges to never block")
        print("• block_duration: How long to block IPs (seconds)")
        print("• log_level: Logging level (DEBUG, INFO, WARNING, ERROR)")
        print(f"\n{Fore.YELLOW}After creating the config file, run the firewall again.{Style.RESET_ALL}")