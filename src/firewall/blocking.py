"""IP blocking and unblocking functionality with cross-platform support"""

import subprocess
import threading
import platform
import tempfile
import shutil
import ipaddress
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Set, List
from colorama import Fore, Style
from utils.logger import get_logger
from utils.system import get_platform_firewall_command


class IPBlocker:
    """Handles IP blocking operations across different platforms"""
    
    def __init__(self, block_duration: int, whitelist: Set[str]):
        self.block_duration = block_duration
        self.whitelist = whitelist
        self.blocked_ips: Dict[str, datetime] = {}
        self.lock = threading.Lock()
        self.logger = get_logger(__name__)
        self.platform = platform.system().lower()
        self.firewall_cmd = get_platform_firewall_command()
        
        # macOS-specific: pfctl configuration
        if self.platform == 'darwin':
            self._init_macos_firewall()

    def _is_valid_ip(self, ip: str) -> bool:
        """Validate IPv4, IPv6, or CIDR ranges"""
        try:
            # Supports IPv4, IPv6 and CIDR (ip_network supports ranges)
            ipaddress.ip_network(ip, strict=False)
            return True
        except ValueError:
            return False


    def block_ip(self, ip: str, reason: str) -> bool:
        """Block an IP address using the appropriate firewall system"""

        # Validate IP before doing anything
        if not self._is_valid_ip(ip):
            self.logger.error(f"Invalid IP address format: {ip}")
            print(f"{Fore.YELLOW}⚠ INVALID IP: {ip}{Style.RESET_ALL}")
            return False

        if self._is_whitelisted(ip):
            self.logger.info(f"IP {ip} is whitelisted, not blocking")
            return False
            
        with self.lock:
            if ip not in self.blocked_ips:
                try:
                    success = self._execute_block_command(ip)
                    
                    if success:
                        self.blocked_ips[ip] = datetime.now()
                        self.logger.warning(f"🚫 BLOCKED IP: {ip} - Reason: {reason}")
                        print(f"{Fore.RED}🚫 BLOCKED: {ip} - {reason}{Style.RESET_ALL}")
                        return True
                    else:
                        self.logger.error(f"Failed to block IP {ip}")
                        return False
                        
                except Exception as e:
                    self.logger.error(f"Exception while blocking IP {ip}: {e}")
                    return False
            else:
                self.logger.debug(f"IP {ip} already blocked")
                return True

    def unblock_ip(self, ip: str) -> bool:
        """Manually unblock a specific IP address"""

        # Validate IP
        if not self._is_valid_ip(ip):
            self.logger.error(f"Invalid IP address format (unblock): {ip}")
            return False

        with self.lock:
            if ip in self.blocked_ips:
                try:
                    success = self._execute_unblock_command(ip)
                    
                    if success:
                        del self.blocked_ips[ip]
                        self.logger.info(f"✅ UNBLOCKED IP: {ip}")
                        print(f"{Fore.GREEN}✅ UNBLOCKED: {ip}{Style.RESET_ALL}")
                        return True
                    else:
                        self.logger.error(f"Failed to unblock IP {ip}")
                        return False
                        
                except Exception as e:
                    self.logger.error(f"Exception while unblocking IP {ip}: {e}")
                    return False
            else:
                self.logger.warning(f"IP {ip} was not blocked")
                return False


    def unblock_expired_ips(self) -> List[str]:
        current_time = datetime.now()
        block_duration = timedelta(seconds=self.block_duration)
        unblocked_ips = []
        
        with self.lock:
            expired_ips = [
                ip for ip, block_time in self.blocked_ips.items()
                if current_time - block_time > block_duration
            ]
            
            for ip in expired_ips:
                if self.unblock_ip(ip):
                    unblocked_ips.append(ip)
        
        return unblocked_ips

    def _is_whitelisted(self, ip: str) -> bool:
        return ip in self.whitelist

    def _execute_block_command(self, ip: str) -> bool:
        try:
            if self.platform == 'linux':
                return self._block_ip_linux(ip)
            elif self.platform == 'darwin':
                return self._block_ip_macos(ip)
            elif self.platform == 'windows':
                return self._block_ip_windows(ip)
            else:
                self.logger.error(f"Blocking not implemented for platform: {self.platform}")
                return False
        except Exception as e:
            self.logger.error(f"Platform-specific blocking failed: {e}")
            return False

    def _execute_unblock_command(self, ip: str) -> bool:
        try:
            if self.platform == 'linux':
                return self._unblock_ip_linux(ip)
            elif self.platform == 'darwin':
                return self._unblock_ip_macos(ip)
            elif self.platform == 'windows':
                return self._unblock_ip_windows(ip)
            else:
                self.logger.error(f"Unblocking not implemented for platform: {self.platform}")
                return False
        except Exception as e:
            self.logger.error(f"Platform-specific unblocking failed: {e}")
            return False


    def _block_ip_linux(self, ip: str) -> bool:
        """Block IPv4 or IPv6 using iptables / ip6tables"""

        try:
            parsed = ipaddress.ip_network(ip, strict=False)

            # IPv6
            if isinstance(parsed, ipaddress.IPv6Network):
                cmd = ['sudo', 'ip6tables', '-A', 'INPUT', '-s', ip, '-j', 'DROP']

            # IPv4
            else:
                cmd = ['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP']

            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return result.returncode == 0

        except Exception as e:
            self.logger.error(f"Linux block error for {ip}: {e}")
            return False

    def _unblock_ip_linux(self, ip: str) -> bool:
        """Unblock IPv4 or IPv6"""

        try:
            parsed = ipaddress.ip_network(ip, strict=False)

            # IPv6
            if isinstance(parsed, ipaddress.IPv6Network):
                cmd = ['sudo', 'ip6tables', '-D', 'INPUT', '-s', ip, '-j', 'DROP']
            # IPv4
            else:
                cmd = ['sudo', 'iptables', '-D', 'INPUT', '-s', ip, '-j', 'DROP']

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception as e:
            self.logger.error(f"Linux unblock error for {ip}: {e}")
            return False


    def _init_macos_firewall(self):
        try:
            pfctl_path = shutil.which('pfctl')
            if not pfctl_path:
                self.logger.warning("pfctl not found.")
                return

            cmd = ['sudo', 'pfctl', '-t', 'blocked_ips', '-T', 'show']
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                subprocess.run(['sudo', 'pfctl', '-t', 'blocked_ips', '-T', 'add', '127.0.0.1'], 
                             capture_output=True, text=True)
                subprocess.run(['sudo', 'pfctl', '-t', 'blocked_ips', '-T', 'delete', '127.0.0.1'], 
                             capture_output=True, text=True)

            cmd = ['sudo', 'pfctl', '-s', 'info']
            result = subprocess.run(cmd, capture_output=True, text=True)
            if 'Status: Enabled' not in result.stdout:
                self.logger.info("Attempting to enable pfctl...")
                subprocess.run(['sudo', 'pfctl', '-e'], capture_output=True, text=True)
            
            self._reload_macos_rules()
            
            self.logger.info("macOS firewall initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize macOS firewall: {e}")
    
    def _reload_macos_rules(self):
        try:
            pf_conf_content = """# Simple Firewall - Dynamic IP Blocking Rules
# This file is managed by Simple Firewall
table <blocked_ips> persist
block drop in quick from <blocked_ips> to any
block drop out quick from any to <blocked_ips>
pass in all
pass out all
"""
            temp_dir = Path(tempfile.gettempdir())
            pf_conf_path = temp_dir / 'simple_firewall_pf.conf'
            
            with open(pf_conf_path, 'w') as f:
                f.write(pf_conf_content)
            
            cmd = ['sudo', 'pfctl', '-f', str(pf_conf_path)]
            subprocess.run(cmd, capture_output=True, text=True)
                
        except Exception as e:
            self.logger.error(f"Failed to reload macOS firewall rules: {e}")
    
    def _block_ip_macos(self, ip: str) -> bool:
        try:
            cmd = ['sudo', 'pfctl', '-t', 'blocked_ips', '-T', 'add', ip]
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return True
            else:
                if 'already' in result.stderr.lower():
                    return True
                return False
        except Exception as e:
            self.logger.error(f"Exception while blocking IP macOS: {e}")
            return False
    
    def _unblock_ip_macos(self, ip: str) -> bool:
        try:
            cmd = ['sudo', 'pfctl', '-t', 'blocked_ips', '-T', 'delete', ip]
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0 or "not found" in result.stderr.lower()
        except Exception as e:
            self.logger.error(f"Exception while unblocking IP macOS: {e}")
            return False

    def _block_ip_windows(self, ip: str) -> bool:
        rule_name = f"SimpleFirewall_Block_{ip.replace('.', '_')}"
        cmd = [
            'netsh', 'advfirewall', 'firewall', 'add', 'rule',
            f'name={rule_name}',
            'dir=in',
            'action=block',
            f'remoteip={ip}'
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Exception running netsh add rule: {e}")
            return False

    def _unblock_ip_windows(self, ip: str) -> bool:
        rule_name = f"SimpleFirewall_Block_{ip.replace('.', '_')}"
        cmd = [
            'netsh', 'advfirewall', 'firewall', 'delete', 'rule',
            f'name={rule_name}'
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            self.logger.error(f"Exception running netsh delete rule: {e}")
            return False


    def get_blocked_ips(self) -> Dict[str, str]:
        with self.lock:
            return {ip: block_time.isoformat() for ip, block_time in self.blocked_ips.items()}
    
    def cleanup_all_blocks(self) -> List[str]:
        cleaned_ips = []
        
        with self.lock:
            for ip in list(self.blocked_ips.keys()):
                if self.unblock_ip(ip):
                    cleaned_ips.append(ip)
        
        
        if self.platform == 'darwin' and cleaned_ips:
            try:
                subprocess.run(['sudo', 'pfctl', '-t', 'blocked_ips', '-T', 'flush'],
                               capture_output=True, text=True)
            except Exception as e:
                self.logger.warning(f"Failed to flush pfctl table: {e}")
        
        return cleaned_ips
    
    def get_stats(self) -> Dict[str, int]:
        with self.lock:
            return {
                'currently_blocked': len(self.blocked_ips),
                'whitelist_size': len(self.whitelist)
            }