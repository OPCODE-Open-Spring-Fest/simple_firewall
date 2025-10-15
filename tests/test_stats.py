"""Test firewall statistics functionality"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from firewall.stats import FirewallStats


class TestFirewallStats:
    """Test firewall statistics tracking"""
    
    def test_initial_state(self):
        """Test initial statistics state"""
        stats = FirewallStats()
        
        assert len(stats.blocked_ips) == 0
        assert stats.packets_analyzed == 0
        assert stats.bytes_analyzed == 0
        assert stats.attacks_blocked == 0
        assert isinstance(stats.start_time, datetime)
    
    def test_record_packet(self):
        """Test packet recording"""
        stats = FirewallStats()
        
        stats.record_packet(1500)  # Record a 1500-byte packet
        
        assert stats.packets_analyzed == 1
        assert stats.bytes_analyzed == 1500
    
    def test_record_attack(self):
        """Test attack recording"""
        stats = FirewallStats()
        
        stats.record_attack("SYN flood", "192.168.1.100")
        
        assert "192.168.1.100" in stats.blocked_ips
        assert stats.attacks_blocked == 1
        assert stats.attack_attempts["SYN flood"] == 1
    
    def test_get_uptime(self):
        """Test uptime calculation"""
        stats = FirewallStats()
        uptime = stats.get_uptime()
        
        assert isinstance(uptime, str)
        assert ":" in uptime  # Should contain time format
    
    def test_get_summary(self):
        """Test statistics summary"""
        stats = FirewallStats()
        
        stats.record_packet(1000)
        stats.record_attack("Port scan", "10.0.0.1")
        
        summary = stats.get_summary()
        
        assert summary['packets_analyzed'] == 1
        assert summary['total_attacks_blocked'] == 1
        assert 'uptime' in summary
        assert 'bytes_analyzed' in summary
        assert 'attack_types' in summary
    
    def test_packets_per_second(self):
        """Test packets per second calculation"""
        stats = FirewallStats()
        
        # Simulate some packet processing
        for _ in range(10):
            stats.record_packet(100)
        
        pps = stats.get_packets_per_second()
        assert pps >= 0  # Should be non-negative
    
    def test_reset_stats(self):
        """Test statistics reset"""
        stats = FirewallStats()
        
        stats.record_packet(1000)
        stats.record_attack("ICMP flood", "172.16.0.1")
        
        stats.reset_stats()
        
        assert stats.packets_analyzed == 0
        assert stats.bytes_analyzed == 0
        assert stats.attacks_blocked == 0
        assert len(stats.attack_attempts) == 0
        # blocked_ips should be preserved
        assert "172.16.0.1" in stats.blocked_ips