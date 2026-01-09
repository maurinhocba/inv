"""
Trading Backtest Framework

A modular framework for backtesting algorithmic trading strategies.

Version: 0.1.2
Author: [Your Name]
Date: 2026-01-08
"""

__version__ = "0.1.2"
__author__ = "[Your Name]"

# Import main classes when available
from .data_manager import DataManager

__all__ = [
    'DataManager',
    # Will add: 'Backtester', 'Portfolio', 'Metrics', etc.
]
