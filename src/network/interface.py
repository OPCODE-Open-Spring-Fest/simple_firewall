"""Network interface detection and management"""

import netifaces
from typing import Optional, List


class NetworkInterface:
    """Handles network interface detection and management"""
    
    def __init__(self, interface: str = None):
        self.interface = interface or self._get_default_interface()
    
    def _get_default_interface(self) -> str:
        """Get the default network interface"""
        try:
            interfaces = netifaces.interfaces()
            
            # Filter out loopback and virtual interfaces
            physical_interfaces = [
                iface for iface in interfaces 
                if not iface.startswith(('lo', 'docker', 'veth', 'br-'))
            ]
            
            # Prefer ethernet interfaces, then wireless
            for iface in physical_interfaces:
                if iface.startswith(('eth', 'en')):
                    return iface
            
            for iface in physical_interfaces:
                if iface.startswith(('wl', 'wlan')):
                    return iface
            
            # Fallback to first available interface
            return physical_interfaces[0] if physical_interfaces else 'eth0'
            
        except Exception:
            return 'eth0'
    
    def get_interface_info(self) -> dict:
        """Get information about the current interface"""
        try:
            addrs = netifaces.ifaddresses(self.interface)
            info = {
                'name': self.interface,
                'ipv4': [],
                'ipv6': [],
                'mac': None
            }
            
            # Get IPv4 addresses
            if netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    info['ipv4'].append({
                        'addr': addr.get('addr'),
                        'netmask': addr.get('netmask'),
                        'broadcast': addr.get('broadcast')
                    })
            
            # Get IPv6 addresses
            if netifaces.AF_INET6 in addrs:
                for addr in addrs[netifaces.AF_INET6]:
                    info['ipv6'].append({
                        'addr': addr.get('addr'),
                        'netmask': addr.get('netmask')
                    })
            
            # Get MAC address
            if netifaces.AF_LINK in addrs:
                info['mac'] = addrs[netifaces.AF_LINK][0].get('addr')
            
            return info
            
        except Exception as e:
            return {'name': self.interface, 'error': str(e)}
    
    def list_all_interfaces(self) -> List[str]:
        """List all available network interfaces"""
        try:
            return netifaces.interfaces()
        except Exception:
            return []
    
    def is_interface_up(self) -> bool:
        """Check if the interface is up and running"""
        try:
            return self.interface in netifaces.interfaces()
        except Exception:
            return False