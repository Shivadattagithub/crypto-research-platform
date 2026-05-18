"""
Position Sizer
--------------
Implements fixed fractional and fractional Kelly criterion
position sizing for systematic strategies.
"""

import numpy as np
import pandas as pd


def fixed_fractional(capital: float, fraction: float, price: float,
                     fee: float = 0.0006) -> float:
    """
    Size a position as a fixed fraction of capital.
    
    Returns the number of units to buy.
    """
    gross_capital = capital * fraction
    net_capital   = gross_capital * (1 - fee)
    return net_capital / price


def kelly_size(win_rate: float, avg_win: float, avg_loss: float,
               fraction: float = 0.25) -> float:
    """
    Fractional Kelly criterion for position sizing.
    
    Args:
        win_rate:  Probability of winning trade (0–1)
        avg_win:   Average gain per winning trade (as fraction, e.g. 0.03)
        avg_loss:  Average loss per losing trade (as positive fraction, e.g. 0.02)
        fraction:  Kelly multiplier — 0.25 = Quarter Kelly (recommended)
    
    Returns:
        Fraction of capital to deploy (0–1)
    """
    if avg_loss == 0:
        return 0.0
    b         = avg_win / avg_loss   # Win/loss ratio
    p         = win_rate
    q         = 1 - p
    full_kelly = (b * p - q) / b
    return max(0.0, full_kelly * fraction)


def compute_kelly_from_returns(returns: pd.Series,
                               fraction: float = 0.25) -> float:
    """Estimate Kelly fraction directly from a returns Series."""
    wins   = returns[returns > 0]
    losses = returns[returns < 0]

    if len(wins) == 0 or len(losses) == 0:
        return 0.0

    win_rate = len(wins) / len(returns)
    avg_win  = wins.mean()
    avg_loss = abs(losses.mean())

    return kelly_size(win_rate, avg_win, avg_loss, fraction)
