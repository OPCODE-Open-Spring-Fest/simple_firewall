#!/bin/bash
# Simple Firewall Installation Script

echo "🛡️  Installing Simple DDoS/DoS Protection Firewall"
echo "=================================================="

# Check if running as root for system-wide installation
if [[ $EUID -eq 0 ]]; then
    echo "⚠️  Running as root - installing system-wide"
    INSTALL_PREFIX="/usr/local/bin"
else
    echo "Installing for current user"
    INSTALL_PREFIX="$HOME/.local/bin"
    mkdir -p "$INSTALL_PREFIX"
fi

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo "✅ Python 3 found: $(python3 --version)"
else
    echo "❌ Python 3 not found. Please install Python 3.6 or later."
    exit 1
fi

# Check if pip is available
echo "Checking pip..."
if command -v pip3 &> /dev/null; then
    echo "✅ pip3 found"
elif command -v pip &> /dev/null; then
    echo "✅ pip found"
else
    echo "❌ pip not found. Please install pip."
    exit 1
fi

# Install Python packages
echo "Installing Python packages..."
if command -v pip3 &> /dev/null; then
    pip3 install --user scapy psutil colorama netifaces
else
    pip install --user scapy psutil colorama netifaces
fi

if [ $? -eq 0 ]; then
    echo "✅ Python packages installed successfully"
else
    echo "❌ Failed to install Python packages"
    exit 1
fi

# Check for iptables
echo "Checking iptables..."
if command -v iptables &> /dev/null; then
    echo "✅ iptables found"
else
    echo "❌ iptables not found. Please install iptables:"
    echo "   Ubuntu/Debian: sudo apt-get install iptables"
    echo "   CentOS/RHEL: sudo yum install iptables"
    exit 1
fi

# Make scripts executable
echo "Setting up scripts..."
chmod +x run.py simple_firewall.py test_attacks.py

# Create a system-wide command (optional)
if [[ $EUID -eq 0 ]]; then
    echo "Creating system-wide commands..."
    
    # Create firewall command
    cat > "$INSTALL_PREFIX/simple-firewall" << 'EOF'
#!/bin/bash
cd "$(dirname "$(readlink -f "$0")")/../share/simple-firewall" || cd "/opt/simple-firewall" || cd "$(pwd)"
exec python3 run.py "$@"
EOF
    chmod +x "$INSTALL_PREFIX/simple-firewall"
    
    # Create installation directory
    mkdir -p /opt/simple-firewall
    cp -r . /opt/simple-firewall/
    
    echo "✅ System-wide installation complete"
    echo "   Run: sudo simple-firewall --start"
else
    # Create user command
    mkdir -p "$HOME/.local/share/simple-firewall"
    cp -r . "$HOME/.local/share/simple-firewall/"
    
    cat > "$INSTALL_PREFIX/simple-firewall" << 'EOF'
#!/bin/bash
cd "$HOME/.local/share/simple-firewall"
exec python3 run.py "$@"
EOF
    chmod +x "$INSTALL_PREFIX/simple-firewall"
    
    echo "✅ User installation complete"
    echo "   Add $HOME/.local/bin to your PATH if needed"
    echo "   Run: sudo simple-firewall --start"
fi

echo ""
echo "🎉 Installation Complete!"
echo "========================="
echo ""
echo "Usage:"
echo "  sudo python3 run.py --start        # Start firewall"
echo "  python3 run.py --stats            # Show statistics"
echo "  python3 run.py --test 127.0.0.1   # Test firewall"
echo ""
echo "Configuration:"
echo "  Edit firewall_config.json to customize thresholds"
echo ""
echo "Documentation:"
echo "  See README.md for detailed usage instructions"
echo ""
echo "⚠️  Remember: This firewall requires root privileges to modify iptables!"
