"""
Trading Strategies Module

Collection of trading strategies for backtesting.

Author: Mauro S. Maza - mauromaza8@gmail.com
Version: 0.2.0
Date: 2026-01-15

Changelog:
- 0.2.0: Added relative_momentum and fip strategies
- 0.1.0: Initial release with price_to_sma_ratio
"""

from .price_to_sma_ratio import price_to_sma_ratio
from .relative_momentum import relative_momentum
from .fip import fip

__all__ = [
    'price_to_sma_ratio',
    'relative_momentum',
    'fip',
]
