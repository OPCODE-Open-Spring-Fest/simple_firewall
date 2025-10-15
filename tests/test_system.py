"""Test system utilities"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from utils.system import (
    get_system_info, 
    check_root_privileges, 
    get_platform_firewall_command,
    format_bytes
)


class TestSystemUtils:
    """Test system utility functions"""
    
    def test_get_system_info(self):
        """Test system information gathering"""
        info = get_system_info()
        
        required_keys = [
            'platform', 'platform_version', 'architecture',
            'python_version', 'cpu_count', 'memory_total', 'disk_usage'
        ]
        
        for key in required_keys:
            assert key in info
        
        assert isinstance(info['cpu_count'], int)
        assert info['cpu_count'] > 0
        assert isinstance(info['memory_total'], int)
        assert info['memory_total'] > 0
    
    def test_check_root_privileges(self):
        """Test privilege checking"""
        # This will vary based on how tests are run
        result = check_root_privileges()
        assert isinstance(result, bool)
    
    def test_get_platform_firewall_command(self):
        """Test platform-specific firewall command detection"""
        cmd = get_platform_firewall_command()
        
        valid_commands = ['iptables', 'pfctl', 'netsh']
        assert cmd in valid_commands
    
    def test_format_bytes(self):
        """Test byte formatting function"""
        assert format_bytes(0) == "0.0 B"
        assert format_bytes(1024) == "1.0 KB"
        assert format_bytes(1024 * 1024) == "1.0 MB"
        assert format_bytes(1024 * 1024 * 1024) == "1.0 GB"
        
        # Test with larger values
        large_value = 1024 * 1024 * 1024 * 1024
        result = format_bytes(large_value)
        assert "TB" in result