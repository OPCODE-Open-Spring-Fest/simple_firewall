"""Configuration data models"""

from dataclasses import dataclass
from typing import List


@dataclass
class AttackSignature:
    """Defines attack patterns and thresholds - loaded from config file"""
    syn_flood_threshold: int      # SYN packets per minute per IP
    connection_threshold: int     # Connection attempts per minute per IP
    packet_rate_threshold: int    # Total packets per minute per IP
    port_scan_threshold: int      # Different ports accessed per minute
    icmp_flood_threshold: int     # ICMP packets per minute per IP


@dataclass
class FirewallConfig:
    """Complete firewall configuration"""
    thresholds: AttackSignature
    whitelist: List[str]
    block_duration: int
    log_level: str
    
    @classmethod
    def from_dict(cls, config_dict: dict) -> 'FirewallConfig':
        """Create FirewallConfig from dictionary"""
        return cls(
            thresholds=AttackSignature(**config_dict['thresholds']),
            whitelist=config_dict.get('whitelist', ['::1', '127.0.0.1']),
            block_duration=config_dict.get('block_duration', 300),
            log_level=config_dict.get('log_level', 'INFO')
        )