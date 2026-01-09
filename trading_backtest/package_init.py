"""
Trading Backtest Framework

A modular framework for backtesting algorithmic trading strategies.

Version: 0.2.1
Author: [Your Name]
Date: 2026-01-09
"""

__version__ = "0.2.1"
__author__ = "[Your Name]"

# Import main classes when available
from .data_manager import DataManager

__all__ = [
    'DataManager',
    # Will add: 'Backtester', 'Portfolio', 'Metrics', etc.
]
