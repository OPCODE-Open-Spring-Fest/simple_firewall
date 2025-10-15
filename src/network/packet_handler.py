"""Packet handling and processing"""

from scapy.all import Packet
from typing import Callable, Optional
from utils.logger import get_logger


class PacketHandler:
    """Handles packet processing and analysis"""
    
    def __init__(self, packet_callback: Callable[[Packet], None]):
        self.packet_callback = packet_callback
        self.logger = get_logger(__name__)
        self.packets_processed = 0
    
    def handle_packet(self, packet: Packet) -> None:
        """Process a single packet"""
        try:
            self.packets_processed += 1
            
            # Log packet info for debugging (only for first few packets)
            if self.packets_processed <= 10:
                self.logger.debug(f"Processing packet #{self.packets_processed}: {packet.summary()}")
            
            # Call the main packet processing callback
            self.packet_callback(packet)
            
        except Exception as e:
            self.logger.error(f"Error processing packet: {e}")
    
    def get_stats(self) -> dict:
        """Get packet processing statistics"""
        return {
            'packets_processed': self.packets_processed
        }