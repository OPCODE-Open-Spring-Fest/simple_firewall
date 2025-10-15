"""Logging utilities and setup"""

import logging
from typing import Optional


def setup_logging(log_level: str = 'INFO') -> logging.Logger:
    """Setup logging configuration"""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('firewall.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('simple_firewall')


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return logging.getLogger(name)