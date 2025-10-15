"""Test configuration loading and validation"""

import pytest
import json
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config.loader import ConfigLoader
from config.models import FirewallConfig, AttackSignature


class TestConfigLoader:
    """Test configuration loading functionality"""
    
    def test_load_valid_config(self):
        """Test loading a valid configuration file"""
        config_data = {
            "thresholds": {
                "syn_flood_threshold": 1000,
                "connection_threshold": 200,
                "packet_rate_threshold": 1000,
                "port_scan_threshold": 80,
                "icmp_flood_threshold": 1000
            },
            "whitelist": ["127.0.0.1", "::1"],
            "block_duration": 300,
            "log_level": "INFO"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            loader = ConfigLoader(config_file)
            config = loader.load_config()
            
            assert isinstance(config, FirewallConfig)
            assert isinstance(config.thresholds, AttackSignature)
            assert config.thresholds.syn_flood_threshold == 1000
            assert config.thresholds.connection_threshold == 200
            assert config.thresholds.packet_rate_threshold == 1000
            assert config.thresholds.port_scan_threshold == 80
            assert config.thresholds.icmp_flood_threshold == 1000
            assert config.block_duration == 300
            assert config.log_level == "INFO"
            assert "127.0.0.1" in config.whitelist
            assert "::1" in config.whitelist
        finally:
            os.unlink(config_file)
    
    def test_load_config_with_defaults(self):
        """Test loading config with missing optional fields"""
        config_data = {
            "thresholds": {
                "syn_flood_threshold": 500,
                "connection_threshold": 100,
                "packet_rate_threshold": 500,
                "port_scan_threshold": 40,
                "icmp_flood_threshold": 500
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            loader = ConfigLoader(config_file)
            config = loader.load_config()
            
            # Verify thresholds are loaded correctly
            assert isinstance(config, FirewallConfig)
            assert isinstance(config.thresholds, AttackSignature)
            assert config.thresholds.syn_flood_threshold == 500
            assert config.thresholds.connection_threshold == 100
            
            # Should use defaults for missing fields
            assert config.block_duration == 300  # default
            assert config.log_level == "INFO"    # default
            assert config.whitelist == ['::1', '127.0.0.1']  # default
        finally:
            os.unlink(config_file)
    
    def test_missing_config_file(self):
        """Test behavior when config file doesn't exist"""
        loader = ConfigLoader("nonexistent_config.json")
        
        with pytest.raises(SystemExit):
            loader.load_config()
    
    def test_invalid_json(self):
        """Test behavior with invalid JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            config_file = f.name
        
        try:
            loader = ConfigLoader(config_file)
            with pytest.raises(SystemExit):
                loader.load_config()
        finally:
            os.unlink(config_file)
    
    def test_missing_thresholds_section(self):
        """Test behavior when thresholds section is completely missing"""
        config_data = {
            "whitelist": ["127.0.0.1"],
            "block_duration": 300,
            "log_level": "INFO"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            loader = ConfigLoader(config_file)
            with pytest.raises(SystemExit):
                loader.load_config()
        finally:
            os.unlink(config_file)
    
    def test_missing_individual_thresholds(self):
        """Test behavior when individual threshold values are missing"""
        config_data = {
            "thresholds": {
                "syn_flood_threshold": 1000,
                "connection_threshold": 200,
                # Missing: packet_rate_threshold, port_scan_threshold, icmp_flood_threshold
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            loader = ConfigLoader(config_file)
            with pytest.raises(SystemExit):
                loader.load_config()
        finally:
            os.unlink(config_file)


class TestFirewallConfig:
    """Test FirewallConfig dataclass"""
    
    def test_from_dict_complete(self):
        """Test creating config from complete dictionary"""
        config_dict = {
            "thresholds": {
                "syn_flood_threshold": 800,
                "connection_threshold": 150,
                "packet_rate_threshold": 800,
                "port_scan_threshold": 60,
                "icmp_flood_threshold": 800
            },
            "whitelist": ["192.168.1.1"],
            "block_duration": 600,
            "log_level": "DEBUG"
        }
        
        config = FirewallConfig.from_dict(config_dict)
        
        assert isinstance(config, FirewallConfig)
        assert isinstance(config.thresholds, AttackSignature)
        assert config.thresholds.syn_flood_threshold == 800
        assert config.thresholds.connection_threshold == 150
        assert config.thresholds.packet_rate_threshold == 800
        assert config.thresholds.port_scan_threshold == 60
        assert config.thresholds.icmp_flood_threshold == 800
        assert config.whitelist == ["192.168.1.1"]
        assert config.block_duration == 600
        assert config.log_level == "DEBUG"
    
    def test_from_dict_with_defaults(self):
        """Test creating config with default values"""
        config_dict = {
            "thresholds": {
                "syn_flood_threshold": 500,
                "connection_threshold": 100,
                "packet_rate_threshold": 500,
                "port_scan_threshold": 40,
                "icmp_flood_threshold": 500
            }
            # Missing optional fields - should use defaults
        }
        
        config = FirewallConfig.from_dict(config_dict)
        
        assert isinstance(config, FirewallConfig)
        assert config.thresholds.syn_flood_threshold == 500
        assert config.whitelist == ['::1', '127.0.0.1']  # default
        assert config.block_duration == 300  # default
        assert config.log_level == 'INFO'  # default


class TestAttackSignature:
    """Test AttackSignature dataclass"""
    
    def test_attack_signature_creation(self):
        """Test creating AttackSignature with all required values"""
        signature = AttackSignature(
            syn_flood_threshold=800,
            connection_threshold=150,
            packet_rate_threshold=800,
            port_scan_threshold=60,
            icmp_flood_threshold=800
        )
        
        assert signature.syn_flood_threshold == 800
        assert signature.connection_threshold == 150
        assert signature.packet_rate_threshold == 800
        assert signature.port_scan_threshold == 60
        assert signature.icmp_flood_threshold == 800