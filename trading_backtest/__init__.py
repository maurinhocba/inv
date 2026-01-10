"""
Trading Backtest Framework

A modular framework for backtesting algorithmic trading strategies.

Version: 0.3.1
Author: [Your Name]
Date: 2026-01-09
"""

__version__ = "0.3.1"
__author__ = "[Your Name]"

# Import main classes
from .data_manager import DataManager
from .portfolio import Portfolio

__all__ = [
    'DataManager',
    'Portfolio',
    # Will add: 'Backtester', 'Metrics', etc.
]
