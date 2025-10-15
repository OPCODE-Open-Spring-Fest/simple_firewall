"""Attack detection algorithms and pattern matching"""

from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Set, Tuple, Optional
from scapy.all import IP, TCP, UDP, ICMP, Packet
from config.models import AttackSignature
from utils.logger import get_logger


class AttackDetector:
    """Handles all attack detection logic"""
    
    def __init__(self, signatures: AttackSignature, whitelist: Set[str]):
        self.signatures = signatures
        self.whitelist = whitelist
        self.logger = get_logger(__name__)
        
        # Tracking dictionaries with time windows (sliding window approach)
        self.ip_packets = defaultdict(lambda: deque())      # Packet count per IP
        self.ip_connections = defaultdict(lambda: deque())  # Connection attempts per IP
        self.ip_ports = defaultdict(lambda: set())          # Ports accessed per IP
        self.ip_syn_packets = defaultdict(lambda: deque())  # SYN packets per IP
        self.ip_icmp_packets = defaultdict(lambda: deque()) # ICMP packets per IP
        self.ip_last_reset = defaultdict(lambda: datetime.now())  # Last reset time for ports
    
    def detect_attacks(self, packet: Packet) -> Optional[Tuple[str, str]]:
        """
        Analyze packet for potential attacks
        
        Args:
            packet: Scapy packet object to analyze
            
        Returns:
            Tuple of (ip, reason) if attack detected, None otherwise
        """
        if not packet.haslayer(IP):
            return None
            
        ip = packet[IP].src
        current_time = datetime.now()
        
        # Skip whitelisted IPs
        if self._is_whitelisted(ip):
            return None
            
        # Clean old entries (sliding window maintenance)
        self._cleanup_old_entries(ip)
        
        # Track this packet
        self.ip_packets[ip].append(current_time)
        
        # Check various attack patterns
        attack_result = (
            self._check_packet_rate(ip) or
            self._check_syn_flood(packet, ip, current_time) or
            self._check_port_scan(packet, ip) or
            self._check_connection_rate(packet, ip, current_time) or
            self._check_icmp_flood(packet, ip, current_time)
        )
        
        if attack_result:
            self.logger.warning(f"Attack detected from {ip}: {attack_result}")
            
        return (ip, attack_result) if attack_result else None
    
    def _is_whitelisted(self, ip: str) -> bool:
        """Check if IP is in whitelist"""
        return ip in self.whitelist
    
    def _cleanup_old_entries(self, ip: str):
        """Clean up old entries from tracking dictionaries (sliding window)"""
        current_time = datetime.now()
        minute_ago = current_time - timedelta(minutes=1)
        
        # Clean packet tracking
        while self.ip_packets[ip] and self.ip_packets[ip][0] < minute_ago:
            self.ip_packets[ip].popleft()
            
        # Clean connection tracking
        while self.ip_connections[ip] and self.ip_connections[ip][0] < minute_ago:
            self.ip_connections[ip].popleft()
            
        # Clean SYN packet tracking
        while self.ip_syn_packets[ip] and self.ip_syn_packets[ip][0] < minute_ago:
            self.ip_syn_packets[ip].popleft()
            
        # Clean ICMP packet tracking  
        while self.ip_icmp_packets[ip] and self.ip_icmp_packets[ip][0] < minute_ago:
            self.ip_icmp_packets[ip].popleft()
        
        # Reset port tracking every minute
        if current_time - self.ip_last_reset[ip] > timedelta(minutes=1):
            self.ip_ports[ip] = set()
            self.ip_last_reset[ip] = current_time
    
    def _check_packet_rate(self, ip: str) -> Optional[str]:
        """Check for high packet rate (general DDoS)"""
        packet_count = len(self.ip_packets[ip])
        if packet_count > self.signatures.packet_rate_threshold:
            return f"High packet rate: {packet_count}/min"
        return None
    
    def _check_syn_flood(self, packet: Packet, ip: str, current_time: datetime) -> Optional[str]:
        """Check for SYN flood attack"""
        if not packet.haslayer(TCP):
            return None
            
        tcp = packet[TCP]
        
        # Check for SYN flag (0x02)
        if tcp.flags & 0x02:  # SYN flag set
            self.ip_syn_packets[ip].append(current_time)
            
            syn_count = len(self.ip_syn_packets[ip])
            if syn_count > self.signatures.syn_flood_threshold:
                return f"SYN flood: {syn_count}/min"
        
        return None
    
    def _check_port_scan(self, packet: Packet, ip: str) -> Optional[str]:
        """Check for port scanning activity"""
        if not packet.haslayer(TCP):
            return None
            
        tcp = packet[TCP]
        
        # Track unique destination ports
        self.ip_ports[ip].add(tcp.dport)
        
        port_count = len(self.ip_ports[ip])
        if port_count > self.signatures.port_scan_threshold:
            return f"Port scan: {port_count} ports"
        
        return None
    
    def _check_connection_rate(self, packet: Packet, ip: str, current_time: datetime) -> Optional[str]:
        """Check for high connection rate"""
        if not packet.haslayer(TCP):
            return None
            
        # Track all TCP connections (not just SYN)
        self.ip_connections[ip].append(current_time)
        
        conn_count = len(self.ip_connections[ip])
        if conn_count > self.signatures.connection_threshold:
            return f"High connection rate: {conn_count}/min"
        
        return None
    
    def _check_icmp_flood(self, packet: Packet, ip: str, current_time: datetime) -> Optional[str]:
        """Check for ICMP flood attack"""
        if not packet.haslayer(ICMP):
            return None
            
        self.ip_icmp_packets[ip].append(current_time)
        
        icmp_count = len(self.ip_icmp_packets[ip])
        if icmp_count > self.signatures.icmp_flood_threshold:
            return f"ICMP flood: {icmp_count}/min"
        
        return None
    
    def get_detection_stats(self) -> Dict[str, int]:
        """Get detection statistics"""
        return {
            'tracked_ips': len(self.ip_packets),
            'total_packets_tracked': sum(len(packets) for packets in self.ip_packets.values()),
            'total_connections_tracked': sum(len(conns) for conns in self.ip_connections.values()),
            'unique_ports_scanned': sum(len(ports) for ports in self.ip_ports.values())
        }