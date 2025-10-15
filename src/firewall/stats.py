"""Firewall statistics tracking and reporting"""

from collections import defaultdict
from datetime import datetime
from typing import Set, Dict, Any
from utils.system import format_bytes


class FirewallStats:
    """Statistics tracking for the firewall"""
    
    def __init__(self):
        self.blocked_ips: Set[str] = set()
        self.attack_attempts = defaultdict(int)
        self.packets_analyzed = 0
        self.start_time = datetime.now()
        self.bytes_analyzed = 0
        self.attacks_blocked = 0
    
    def get_uptime(self) -> str:
        """Get formatted uptime string"""
        uptime = datetime.now() - self.start_time
        return str(uptime).split('.')[0]  # Remove microseconds
    
    def record_packet(self, packet_size: int = 0):
        """Record a processed packet"""
        self.packets_analyzed += 1
        self.bytes_analyzed += packet_size
    
    def record_attack(self, attack_type: str, ip: str):
        """Record an attack attempt"""
        self.attack_attempts[attack_type] += 1
        self.blocked_ips.add(ip)
        self.attacks_blocked += 1
    
    def get_summary(self) -> Dict[str, Any]:
        """Get comprehensive statistics summary"""
        return {
            'uptime': self.get_uptime(),
            'packets_analyzed': self.packets_analyzed,
            'bytes_analyzed': format_bytes(self.bytes_analyzed),
            'currently_blocked_ips': len(self.blocked_ips),
            'total_attacks_blocked': self.attacks_blocked,
            'attack_types': dict(self.attack_attempts),
            'start_time': self.start_time.isoformat()
        }
    
    def get_packets_per_second(self) -> float:
        """Calculate average packets per second"""
        uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        return self.packets_analyzed / uptime_seconds if uptime_seconds > 0 else 0
    
    def reset_stats(self):
        """Reset all statistics (keeping blocked IPs)"""
        self.packets_analyzed = 0
        self.bytes_analyzed = 0
        self.attacks_blocked = 0
        self.attack_attempts.clear()
        self.start_time = datetime.now()