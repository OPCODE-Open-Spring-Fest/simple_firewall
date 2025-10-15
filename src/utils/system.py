"""System utilities and helpers"""

import os
import platform
import psutil
from typing import Dict, Any


def get_system_info() -> Dict[str, Any]:
    """Get system information"""
    return {
        'platform': platform.system(),
        'platform_version': platform.version(),
        'architecture': platform.architecture()[0],
        'python_version': platform.python_version(),
        'cpu_count': psutil.cpu_count(),
        'memory_total': psutil.virtual_memory().total,
        'disk_usage': psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
    }


def check_root_privileges() -> bool:
    """Check if running with root/admin privileges"""
    if os.name == 'nt':  # Windows
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:  # Unix-like systems
        return os.geteuid() == 0


def get_platform_firewall_command() -> str:
    """Get the appropriate firewall command for the current platform"""
    system = platform.system().lower()
    
    if system == 'linux':
        return 'iptables'
    elif system == 'darwin':  # macOS
        return 'pfctl'
    elif system == 'windows':
        return 'netsh'
    else:
        raise NotImplementedError(f"Firewall commands not implemented for {system}")


def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"