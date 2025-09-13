"""
Logging configuration for FraudShield AI Service
"""

import logging
import sys
from datetime import datetime
from typing import Optional

def setup_logger(name: str, level: str = "INFO") -> logging.Logger:
    """
    Setup logger with consistent formatting
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    # Set logging level
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(numeric_level)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger

def get_logger(name: str) -> logging.Logger:
    """Get logger instance"""
    return logging.getLogger(name)

class LoggerMixin:
    """Mixin class to add logging capabilities to any class"""
    
    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class"""
        return get_logger(self.__class__.__name__)
    
    def log_info(self, message: str, **kwargs):
        """Log info message"""
        self.logger.info(message, extra=kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(message, extra=kwargs)
    
    def log_error(self, message: str, **kwargs):
        """Log error message"""
        self.logger.error(message, extra=kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(message, extra=kwargs)
