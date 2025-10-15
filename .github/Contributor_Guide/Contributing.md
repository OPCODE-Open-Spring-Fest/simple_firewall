# Contributing to Simple Firewall

Thank you for taking the time to contribute to Simple Firewall! We really appreciate it. This project aims to create an educational DDoS/DoS protection firewall with a user-friendly GUI interface.

Before contributing, please make sure to read the [Code of Conduct](../../CODE_OF_CONDUCT.md). We expect you to follow it in all your interactions with the project.

## New to Simple Firewall?

If you are new to Simple Firewall, please take a look at the [Project Tour](./Project_Tour.md) documentation. It's a great place to start understanding the codebase structure and architecture.

## New Contributor Guide

To get an overview of the project:
1. Read the main [README.md](../../README.md) for project overview
2. Check out the [Project Tour](./Project_Tour.md) for detailed code walkthrough
3. Review the [firewall_config.json](../../firewall_config.json) to understand configuration options
4. Explore the new modular structure in [src/](../../src/) directory:
   - `src/firewall/core.py` - Main firewall orchestration
   - `src/config/loader.py` - Configuration management
   - `src/network/packet_handler.py` - Network packet processing
   - `main.py` - Modern CLI entry point

## Development Environment Setup

### Prerequisites

#### All Platforms
- **Python 3.8+** (recommended 3.10+)
- **Node.js 16+** (for commit hooks and future GUI development)
- **Git** for version control

#### Linux (Primary Development Platform)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv nodejs npm

# Arch Linux
sudo pacman -S python python-pip nodejs npm

# CentOS/RHEL
sudo yum install python3 python3-pip nodejs npm
```

#### macOS
```bash
# Using Homebrew
brew install python3 node

# Install Xcode Command Line Tools (required for some Python packages)
xcode-select --install
```

#### Windows
```powershell
# Using Chocolatey (recommended)
choco install python nodejs

# Or download from official websites:
# Python: https://python.org/downloads
# Node.js: https://nodejs.org/downloads
```

### Project Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/simple_firewall.git
   cd simple_firewall
   ```

2. **Set up Python Environment**
   ```bash
   # Create virtual environment
   python3 -m venv venv
   
   # Activate virtual environment
   # Linux/macOS:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Install Development Tools**
   ```bash
   # Install Node.js dependencies (for commit hooks)
   npm install
   
   # This will set up Husky git hooks automatically
   ```

4. **Create Configuration File**
   ```bash
   # Generate configuration template with the new CLI
   python3 main.py --create-config
   
   # Edit configuration as needed
   nano firewall_config.json
   ```

### Platform-Specific Notes

#### Linux
- Requires `sudo` privileges for iptables operations
- Install libpcap development headers:
  ```bash
  # Ubuntu/Debian
  sudo apt install libpcap-dev
  # Arch Linux  
  sudo pacman -S libpcap
  ```

#### macOS
- Uses `pfctl` instead of `iptables` (implementation needed)
- Install libpcap via Homebrew:
  ```bash
  brew install libpcap
  ```
- May require running with `sudo` for packet capture

#### Windows
- Requires Npcap or WinPcap for packet capture
- Uses Windows Firewall API instead of iptables (implementation needed)
- Install Npcap: https://npcap.org/

## How to Contribute

### Reporting Bugs

Found a bug? Please help us by [creating an issue](https://github.com/OPCODE-Open-Spring-Fest/simple_firewall/issues/new) with:

- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, etc.)
- **Log files** if applicable (`firewall.log`)
- **Configuration file** (remove sensitive data)

### Suggesting Features

Have an idea for improvement? We'd love to hear it! Please [create a feature request](https://github.com/OPCODE-Open-Spring-Fest/simple_firewall/issues/new) with:

- **Clear description** of the feature
- **Use case** - why would this be useful?
- **Proposed implementation** (if you have ideas)
- **Alternative solutions** you've considered

### Pull Request Process

1. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

2. **Follow Coding Standards**
   - Use **type hints** for all functions
   - Follow **PEP 8** style guide
   - Add **docstrings** to classes and functions
   - Write **unit tests** for new features
   - Update **documentation** as needed

3. **Commit Your Changes**
   ```bash
   # Our commit hooks will validate your message format
   git commit -m "feat: add GUI dashboard component"
   git commit -m "fix: resolve packet capture on macOS"
   git commit -m "docs: update installation instructions"
   ```

4. **Test Your Changes**
   ```bash
   # Run comprehensive test suite
   make test  # or python -m pytest tests/ -v
   
   # Test the firewall with new CLI
   sudo python3 main.py
   
   # Test configuration management
   python3 main.py --create-config
   python3 main.py --stats
   
   # Test attack simulation
   python3 tools/attack_simulator.py
   ```

5. **Create Pull Request**
   - Use the provided PR template
   - Reference related issues with `Fixes #123`
   - Include screenshots for GUI changes
   - Ensure all checks pass

## Development Guidelines

### Code Style

- **Language**: Python 3.8+ with type hints
- **Formatting**: Black formatter (line length: 88)
- **Linting**: Flake8 with standard configuration
- **Import sorting**: isort

### Commit Convention

We follow [Conventional Commits](https://conventionalcommits.org/):

- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code formatting (no logic changes)
- `refactor:` Code restructuring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

### Testing

- Write unit tests for new functions
- Use `pytest` framework
- Aim for >80% code coverage
- Include integration tests for major features

### Documentation

- Update docstrings for new/modified functions
- Add type hints to all function signatures
- Update README.md for new features
- Include code examples in documentation

## Current Development Priorities

### Phase 1: Core Stability (Current)
- [ ] Cross-platform compatibility (macOS, Windows)
- [ ] Improved error handling and logging
- [ ] Unit test coverage
- [ ] Performance optimizations

### Phase 2: GUI Development (Upcoming)
- [ ] Web-based dashboard (Flask/FastAPI + React)
- [ ] Real-time statistics visualization
- [ ] Configuration management interface
- [ ] Alert and notification system

### Phase 3: Advanced Features (Future)
- [ ] Machine learning-based attack detection
- [ ] Geographic IP analysis
- [ ] Custom rule engine
- [ ] API for external integrations

## Getting Help

- **Questions?** Open a [discussion](https://github.com/OPCODE-Open-Spring-Fest/simple_firewall/discussions)
- **Chat**: Join our community discussions
- **Email**: Contact maintainers for security issues

## Recognition

Contributors will be:
- Listed in our [README.md](../../README.md) contributors section
- Mentioned in release notes for significant contributions
- Invited to join the core team for consistent contributors

Thank you for contributing to Simple Firewall! 🛡️

