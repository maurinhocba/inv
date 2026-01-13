"""
Metrics Module

Calculates performance metrics for backtesting results.

Author: Mauro S. Maza - mauromaza8@gmail.com
Version: 0.1.0
Date: 2026-01-09
"""

import numpy as np
import pandas as pd


def calculate_metrics(history_df, initial_capital):
    """
    Calculate performance metrics from backtest history.
    
    Args:
        history_df (DataFrame): Backtest history with columns:
                               [date, portfolio_value, cash, num_positions, ...]
        initial_capital (float): Starting capital
    
    Returns:
        dict: Performance metrics
    """
    if history_df.empty:
        raise ValueError("Cannot calculate metrics from empty history")
    
    final_value = history_df['portfolio_value'].iloc[-1]
    
    # Calculate returns
    total_return = (final_value - initial_capital) / initial_capital
    
    # Calculate annualized return (TIR/IRR)
    days = (history_df['date'].iloc[-1] - history_df['date'].iloc[0]).days
    years = days / 365.25
    
    if years > 0:
        tir = (final_value / initial_capital) ** (1 / years) - 1
    else:
        tir = 0
    
    # Calculate daily returns for volatility and Sharpe
    daily_returns = history_df['portfolio_value'].pct_change().dropna()
    
    if len(daily_returns) > 1:
        # Annualized volatility (assuming daily data)
        volatility = daily_returns.std() * np.sqrt(252)  # 252 trading days
        
        # Sharpe ratio (assuming risk-free rate = 0)
        # Annual return / annual volatility
        if volatility > 0:
            sharpe = tir / volatility
        else:
            sharpe = 0
    else:
        volatility = 0
        sharpe = 0
    
    # Calculate maximum drawdown
    cummax = history_df['portfolio_value'].cummax()
    drawdown = (history_df['portfolio_value'] - cummax) / cummax
    max_drawdown = drawdown.min()
    
    # Number of rebalances
    num_rebalances = len(history_df)
    
    return {
        'final_value': final_value,
        'total_return': total_return,
        'tir': tir,
        'sharpe': sharpe,
        'max_drawdown': max_drawdown,
        'volatility': volatility,
        'num_rebalances': num_rebalances,
        'days': days,
        'years': years
    }


def calculate_rolling_sharpe(history_df, window=60):
    """
    Calculate rolling Sharpe ratio.
    
    Args:
        history_df (DataFrame): Backtest history
        window (int): Rolling window size in days
    
    Returns:
        pd.Series: Rolling Sharpe ratio
    """
    returns = history_df['portfolio_value'].pct_change()
    rolling_mean = returns.rolling(window).mean()
    rolling_std = returns.rolling(window).std()
    
    rolling_sharpe = (rolling_mean / rolling_std) * np.sqrt(252)
    
    return rolling_sharpe


def calculate_drawdown_series(history_df):
    """
    Calculate drawdown series.
    
    Args:
        history_df (DataFrame): Backtest history
    
    Returns:
        pd.Series: Drawdown at each point
    """
    cummax = history_df['portfolio_value'].cummax()
    drawdown = (history_df['portfolio_value'] - cummax) / cummax
    
    return drawdown


def compare_strategies(results_list, strategy_names=None):
    """
    Compare multiple backtest results.
    
    Args:
        results_list (list): List of backtest result dicts
        strategy_names (list, optional): Names for each strategy
    
    Returns:
        pd.DataFrame: Comparison table
    """
    if strategy_names is None:
        strategy_names = [f"Strategy {i+1}" for i in range(len(results_list))]
    
    comparison = []
    
    for name, results in zip(strategy_names, results_list):
        metrics = results['metrics']
        comparison.append({
            'Strategy': name,
            'Final Value': metrics['final_value'],
            'Total Return %': metrics['total_return'] * 100,
            'Annual Return %': metrics['tir'] * 100,
            'Sharpe Ratio': metrics['sharpe'],
            'Max Drawdown %': metrics['max_drawdown'] * 100,
            'Volatility %': metrics['volatility'] * 100,
            'Rebalances': metrics['num_rebalances']
        })
    
    df = pd.DataFrame(comparison)
    return df
