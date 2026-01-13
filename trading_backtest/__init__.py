"""
Trading Backtest Framework

A modular framework for backtesting algorithmic trading strategies.

Version: 0.4.1
Author: Mauro S. Maza - mauromaza8@gmail.com
Date: 2026-01-09
"""

__version__ = "0.4.1"
__author__ = "Mauro S. Maza - mauromaza8@gmail.com"

# Import main classes
from .data_manager import DataManager
from .portfolio import Portfolio
from .backtester import Backtester
from . import strategies
from . import metrics

__all__ = [
    'DataManager',
    'Portfolio',
    'Backtester',
    'strategies',
    'metrics',
]
