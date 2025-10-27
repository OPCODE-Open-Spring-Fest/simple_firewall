# src/network/interface.py
"""Network interface detection and management"""

import netifaces
import platform
from typing import Optional, List

# Use psutil on Windows to get friendly interface names
try:
    import psutil
except Exception:
    psutil = None


class NetworkInterface:
    """Handles network interface detection and management"""

    def __init__(self, interface: str = None):
        self._platform = platform.system().lower()
        self.interface = interface or self._get_default_interface()

    def _get_default_interface(self) -> str:
        """Get the default network interface (Windows-friendly names when available)"""
        try:
            # On Windows prefer psutil names (friendly names)
            if self._platform == 'windows' and psutil is not None:
                # psutil returns a mapping of friendly names
                names = [name for name in psutil.net_if_addrs().keys()
                         if not name.startswith(('Loopback', 'loopback', 'vEthernet'))]
                # Prefer "Ethernet" or "Wi-Fi" heuristically
                for n in names:
                    if n.lower().startswith('ether') or 'ethernet' in n.lower():
                        return n
                for n in names:
                    if 'wi' in n.lower() or 'wifi' in n.lower() or 'wi-fi' in n.lower():
                        return n
                return names[0] if names else 'Ethernet'
            else:
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
            return ''

    def get_interface_info(self) -> dict:
        """Get information about the current interface"""
        try:
            addrs = netifaces.ifaddresses(self.interface) if self.interface else {}
            info = {
                'name': self.interface,
                'ipv4': [],
                'ipv6': [],
                'mac': None
            }

            # Get IPv4 addresses
            if addrs and netifaces.AF_INET in addrs:
                for addr in addrs[netifaces.AF_INET]:
                    info['ipv4'].append({
                        'addr': addr.get('addr'),
                        'netmask': addr.get('netmask'),
                        'broadcast': addr.get('broadcast')
                    })

            # Get IPv6 addresses
            if addrs and netifaces.AF_INET6 in addrs:
                for addr in addrs[netifaces.AF_INET6]:
                    info['ipv6'].append({
                        'addr': addr.get('addr'),
                        'netmask': addr.get('netmask')
                    })

            # Get MAC address
            if addrs and netifaces.AF_LINK in addrs:
                info['mac'] = addrs[netifaces.AF_LINK][0].get('addr')

            return info

        except Exception as e:
            return {'name': self.interface, 'error': str(e)}

    @staticmethod
    def list_all_interfaces() -> List[str]:
        """List all available network interfaces (friendly names preferred on Windows)"""
        try:
            current_platform = platform.system().lower()
            if current_platform == 'windows' and psutil is not None:
                return list(psutil.net_if_addrs().keys())
            return netifaces.interfaces()
        except Exception:
            return []

    def is_interface_up(self) -> bool:
        """Check if the interface is up and running"""
        try:
            if self._platform == 'windows' and psutil is not None:
                return self.interface in psutil.net_if_stats()
            return self.interface in netifaces.interfaces()
        except Exception:
            return False