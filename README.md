# Simple DDoS/DoS Protection Firewall

A lightweight, educational firewall that demonstrates basic network attack detection and blocking mechanisms for Linux systems.

**⚠️ Important Notice:** This is an educational/proof-of-concept project. It provides basic protection against simple attacks but should NOT be used as a primary security solution in production environments.

## Project Approach

This firewall uses a **threshold-based detection approach**:

1. **Packet Capture**: Uses Scapy to monitor network packets in real-time
2. **Pattern Analysis**: Counts packets, connections, and ports per IP address over time windows
3. **Threshold Comparison**: Blocks IPs when activity exceeds predefined limits
4. **Automatic Blocking**: Uses Linux iptables to drop traffic from malicious IPs
5. **Time-based Recovery**: Automatically unblocks IPs after a timeout period

### Detection Methods
- **SYN Flood**: Counts TCP SYN packets per IP per minute
- **Port Scanning**: Tracks unique ports accessed by each IP
- **ICMP Flood**: Monitors ICMP packet rates per IP
- **Connection Flooding**: Counts connection attempts per IP
- **General Rate Limiting**: Monitors overall packet rates per IP

## Basic Features

🛡️ **Simple Attack Detection:**
- Basic SYN flood detection
- Elementary port scan detection  
- ICMP flood monitoring
- Connection rate limiting
- Packet rate monitoring

🚫 **Basic Protection:**
- IP blocking via iptables (Linux only)
- Configurable detection thresholds
- Temporary blocking with auto-unblock
- IP whitelist support
- Basic logging

📊 **Simple Monitoring:**
- Real-time attack alerts
- Basic statistics display
- Simple log file output

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create configuration file:**
   ```bash
   python3 main.py --create-config
   ```

3. **Start the firewall:**
   ```bash
   sudo python3 main.py
   ```
   **Note on Virtual Environments:** When using a virtual environment (like `venv`), `sudo` does not use your virtual environment's path. You must provide the full path to the Python executable inside your `venv` folder. For example:
   ```bash
   sudo ./venv/bin/python3 main.py
   ```

4. **Test the firewall** (in another terminal):
   ```bash
   python3 test_attacks.py 127.0.0.1
   ```

## Usage

### Basic Commands

```bash
# Show help and usage
python3 main.py --help

# Start firewall with default settings
sudo python3 main.py

# Monitor specific network interface
sudo python3 main.py -i eth0

# Use custom configuration file
sudo python3 main.py -c my_config.json

# Show network statistics
python3 main.py --stats

# Create sample configuration
python3 main.py --create-config

# Run with verbose logging
sudo python3 main.py -v
```

### Legacy Commands (Deprecated)

```bash
# Old run.py launcher (redirects to main.py)
python3 run.py

# Old direct firewall (moved to simple_firewall_old.py)
# sudo python3 simple_firewall.py  # NO LONGER AVAILABLE
```


## Configuration

Edit `firewall_config.json` to customize thresholds:

```json
{
    "thresholds": {
        "syn_flood_threshold": 100,     // SYN packets per minute
        "connection_threshold": 50,      // Connections per IP per minute
        "packet_rate_threshold": 1000,   // Total packets per IP per minute
        "port_scan_threshold": 20,       // Different ports accessed per minute
        "icmp_flood_threshold": 100      // ICMP packets per minute
    },
    "whitelist": [
        "127.0.0.1",                    // Always allow localhost
        "192.168.1.1"                   // Add trusted IPs here
    ],
    "block_duration": 300,              // Block duration in seconds (5 minutes)
    "log_level": "INFO"                 // Logging level
}
```

## Architecture & Implementation

### **New Modular Architecture (v2.0)**

The firewall has been completely restructured into a **modular, maintainable architecture**:

#### **🏗️ Key Benefits:**
- ✅ **Cross-Platform Ready:** Framework for Windows/macOS support
- ✅ **Testable:** Comprehensive unit test coverage
- ✅ **Maintainable:** Single responsibility principle
- ✅ **Extensible:** Easy to add new features
- ✅ **GUI-Ready:** Clean separation for web dashboard
- ✅ **Developer-Friendly:** Clear code organization

#### **🔧 Component Architecture:**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   main.py       │    │ Network         │    │ Attack          │
│   Entry Point   │───▶│ Interface       │───▶│ Detection       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Configuration   │    │ Packet          │    │ IP Blocking     │
│ Management      │    │ Handler         │    │ (Cross-Platform)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **Detection Algorithm (Threshold-Based Approach)**

The firewall operates on a simple **sliding window** principle:

1. **Data Collection Phase:**
   ```python
   # For each IP address, track:
   ip_packets[ip] = deque()          # All packets with timestamps
   ip_syn_packets[ip] = deque()      # SYN packets only  
   ip_connections[ip] = deque()      # Connection attempts
   ip_ports[ip] = set()              # Unique ports accessed
   ip_icmp_packets[ip] = deque()     # ICMP packets
   ```

2. **Time Window Management:**
   - Uses **1-minute sliding windows** for all detection
   - Automatically removes data older than 60 seconds
   - Resets port tracking every minute per IP

3. **Threshold Evaluation:**
   ```python
   # Example: SYN flood detection
   if len(ip_syn_packets[ip]) > syn_flood_threshold:
       block_ip(ip, "SYN flood detected")
   ```

4. **Blocking Mechanism:**
   ```bash
   # Adds iptables rule to drop all traffic from IP
   iptables -A INPUT -s [MALICIOUS_IP] -j DROP
   ```

### **Why This Approach Has Limitations:**

1. **No Behavioral Learning:** Cannot distinguish between legitimate bulk transfers and attacks
2. **Fixed Time Windows:** All attacks use same 1-minute window regardless of attack type
3. **Simple Counting:** No statistical analysis or anomaly detection
4. **No Context Awareness:** Doesn't consider normal traffic patterns for each IP
5. **Memory Inefficient:** Stores all packet timestamps instead of using rolling statistics

### **Attack Detection Workflow:**
```
Packet Received → Extract IP → Update Counters → Check Thresholds → Block if Exceeded
     ↓               ↓              ↓                ↓                    ↓
  Scapy Capture → IP Analysis → Sliding Window → Threshold Compare → iptables Block
```

## Project Structure

### **Core Files:**
- `main.py` - **NEW:** Modern entry point with comprehensive CLI
- `firewall_config.json` - Configuration file with validation
- `firewall.log` - Activity log file (auto-created)
- `requirements.txt` - Python dependencies

### **Modular Source Code (`src/`):**
```
src/
├── firewall/                  # Core firewall components
│   ├── core.py               # Main orchestration
│   ├── detection.py          # Attack detection algorithms
│   ├── blocking.py           # Cross-platform IP blocking
│   └── stats.py              # Statistics tracking
├── config/                    # Configuration management
│   ├── models.py             # Data models & validation
│   └── loader.py             # Config loading with templates
├── network/                   # Network handling
│   ├── interface.py          # Interface detection
│   └── packet_handler.py     # Packet processing
└── utils/                     # Utilities
    ├── logger.py             # Logging system
    └── system.py             # System utilities
```

### **Testing & Tools:**
- `tests/` - Comprehensive unit test suite
- `test_attacks.py` - Attack simulation for testing
- `.github/` - GitHub workflows and documentation

### **Legacy Files:**
- `simple_firewall_old.py` - Original monolithic implementation (backup)
- `run.py` - Legacy launcher (redirects to main.py)

## Requirements

- **Python 3.6+**
- **Root privileges** (required for iptables access)
- **Linux system** (uses iptables for blocking)

### Python Packages:
- `scapy` - Packet capture and analysis
- `psutil` - System and network statistics
- `colorama` - Colored terminal output  
- `netifaces` - Network interface detection

## Testing

The included test script can simulate various types of attacks:

```bash
# Simulate all attack types
sudo python3 test_attacks.py 127.0.0.1

# Specific attack types
sudo python3 test_attacks.py 127.0.0.1 --attack-type syn
sudo python3 test_attacks.py 127.0.0.1 --attack-type port
sudo python3 test_attacks.py 127.0.0.1 --attack-type icmp

# Custom duration and port
sudo python3 test_attacks.py 192.168.1.100 --port 8080 --duration 60
```

**⚠️ Warning:** Only test against systems you own or have explicit permission to test!

## Monitoring and Logs

The firewall provides several ways to monitor activity:

### Real-time Display
- Attack alerts with color coding
- Statistics updated every minute
- Currently blocked IPs
- Attack type breakdown

### Log Files
Check `firewall.log` for detailed activity:
```bash
tail -f firewall.log
```

### Network Statistics
```bash
python3 main.py --stats
```

## Troubleshooting

### Permission Errors
```bash
# Make sure to run with sudo
sudo python3 main.py
```

### Interface Detection Issues
```bash
# List available interfaces
ip link show

# Specify interface in firewall_config.json
"interface": "eth0"
```

### Blocked Legitimate Traffic
- Add trusted IPs to whitelist in config
- Adjust thresholds if too sensitive
- Check `firewall.log` for blocking reasons

### Unblocking IPs Manually
```bash
# List current iptables rules
sudo iptables -L INPUT -n

# Remove specific rule
sudo iptables -D INPUT -s [IP_ADDRESS] -j DROP

# Clear all INPUT rules (use with caution)
sudo iptables -F INPUT
```

## Current Limitations & Known Issues

⚠️ **Platform Limitations:**
- **Linux Only:** Currently only works on Linux systems with iptables
- **No Windows/macOS Support:** Would require complete rewrite of blocking mechanism
- **IPv4 Only:** No IPv6 support implemented
- **Single Interface:** Can only monitor one network interface at a time

🔍 **Detection Limitations:**
- **Threshold-Based Only:** Uses simple packet counting, not behavioral analysis
- **False Positives:** May block legitimate high-traffic users
- **No Deep Packet Inspection:** Only analyzes packet headers, not content
- **Time Window Fixed:** 1-minute detection windows cannot be customized per attack type

🛡️ **Security Limitations:**
- **Bypass Methods:** Attackers can rotate IPs to evade blocking
- **Resource Consumption:** High CPU usage during packet analysis
- **Memory Growth:** Tracking dictionaries can grow large over time
- **No Encrypted Traffic Analysis:** Cannot inspect HTTPS/encrypted packets
- **Limited Attack Types:** Only detects basic flood-style attacks

🔧 **Technical Limitations:**
- **Root Privileges Required:** Must run as root for iptables access
- **No GUI:** Command-line interface only
- **Basic Configuration:** Limited customization options
- **No Database:** All data stored in memory (lost on restart)
- **Single-Threaded Analysis:** Packet processing may become bottleneck

## Educational Value vs Production Use

### ✅ **Good for Learning:**
- Understanding basic network security concepts
- Learning packet analysis with Scapy
- Demonstrating firewall automation principles
- Teaching threshold-based detection methods

### ❌ **Not Suitable for Production:**
- **Missing Advanced Features:** No geo-blocking, reputation databases, or ML detection
- **Limited Scalability:** Cannot handle high-traffic environments
- **Security Gaps:** Many attack vectors not covered
- **No Enterprise Features:** No centralized management, reporting, or integration APIs

## Contributing

This is an **educational open-source project** designed to help people learn network security concepts. Contributions are welcome!

### 🎯 **Project Goals:**
- **Educational Focus:** Help students and developers understand network security
- **Simple Implementation:** Keep code readable and well-documented
- **Cross-Platform Support:** Extend beyond Linux to Windows/macOS
- **Modern Detection:** Add ML-based attack detection methods

### 🚀 **Contribution Ideas:**
- **Windows/macOS Support:** Implement platform-specific firewall backends
- **GUI Interface:** Create a web dashboard or desktop GUI
- **Better Detection:** Add behavioral analysis or ML models  
- **Performance:** Optimize packet processing and memory usage
- **Testing:** Add unit tests and integration tests
- **Documentation:** Improve code comments and examples

### 📋 **Current Architecture Issues to Fix:**
- Replace hardcoded magic numbers with named constants
- Improve error handling and logging
- Add input validation and sanitization
- Implement proper configuration validation
- Add database persistence for attack data
- Create modular plugin system for new attack types

### 🔧 **Development Setup:**
```bash
# Clone and setup development environment
git clone https://github.com/OPCODE-Open-Spring-Fest/simple_firewall.git
cd simple_firewall

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install development tools (optional)
npm install  # For commit hooks

# Create configuration
python3 main.py --create-config

# Run tests
python3 -m pytest tests/ -v

# Development workflow
make help          # Show all commands  
make test          # Run unit tests (20+ comprehensive tests)
make test-verbose  # Detailed test output
make dev           # Development mode (no sudo needed)
make clean         # Clean temporary files
```

## Security Notes

- This is a **basic educational firewall** for learning purposes
- **DO NOT use in production environments** without significant improvements
- Should be used alongside proper security measures in any real deployment
- Test thoroughly in isolated environments only
- Monitor logs regularly for false positives when experimenting
- Keep whitelist updated with trusted IPs during testing

## License

This project is provided as-is for educational and research purposes. Use responsibly and only on systems you own or have explicit permission to test.
