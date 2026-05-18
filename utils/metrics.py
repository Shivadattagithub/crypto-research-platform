"""
Performance Metrics
--------------------
Calculates key quantitative performance statistics for strategy evaluation.
All metrics are annualised assuming 365 trading days (crypto markets).
"""

import numpy as np
import pandas as pd

TRADING_DAYS = 365


def sharpe_ratio(returns: pd.Series, risk_free: float = 0.0) -> float:
    """Annualised Sharpe ratio."""
    excess = returns - risk_free / TRADING_DAYS
    if excess.std() == 0:
        return 0.0
    return float((excess.mean() / excess.std()) * np.sqrt(TRADING_DAYS))


def sortino_ratio(returns: pd.Series, risk_free: float = 0.0) -> float:
    """Annualised Sortino ratio — penalises only downside volatility."""
    excess   = returns - risk_free / TRADING_DAYS
    downside = excess[excess < 0]
    if len(downside) == 0 or downside.std() == 0:
        return 0.0
    return float((excess.mean() / downside.std()) * np.sqrt(TRADING_DAYS))


def calmar_ratio(returns: pd.Series) -> float:
    """Calmar ratio — annualised return divided by max drawdown."""
    ann_return = annualised_return(returns)
    mdd        = max_drawdown(returns)
    if mdd == 0:
        return 0.0
    return float(ann_return / abs(mdd))


def max_drawdown(returns: pd.Series) -> float:
    """Maximum peak-to-trough drawdown as a fraction."""
    equity      = (1 + returns).cumprod()
    rolling_max = equity.cummax()
    drawdown    = (equity - rolling_max) / rolling_max
    return float(drawdown.min())


def annualised_return(returns: pd.Series) -> float:
    """Compound annualised growth rate."""
    total   = (1 + returns).prod()
    n_years = len(returns) / TRADING_DAYS
    if n_years == 0:
        return 0.0
    return float(total ** (1 / n_years) - 1)


def win_rate(returns: pd.Series) -> float:
    """Fraction of periods with positive returns."""
    if len(returns) == 0:
        return 0.0
    return float((returns > 0).sum() / len(returns))


def profit_factor(returns: pd.Series) -> float:
    """Gross profit divided by gross loss."""
    gains  = returns[returns > 0].sum()
    losses = abs(returns[returns < 0].sum())
    if losses == 0:
        return float("inf")
    return float(gains / losses)


def full_report(returns: pd.Series, positions: pd.Series = None) -> dict:
    """Generate a complete performance report dictionary."""
    report = {
        "Total Return"      : f"{(1 + returns).prod() - 1:+.2%}",
        "Annualised Return" : f"{annualised_return(returns):+.2%}",
        "Sharpe Ratio"      : f"{sharpe_ratio(returns):.3f}",
        "Sortino Ratio"     : f"{sortino_ratio(returns):.3f}",
        "Calmar Ratio"      : f"{calmar_ratio(returns):.3f}",
        "Max Drawdown"      : f"{max_drawdown(returns):.2%}",
        "Win Rate"          : f"{win_rate(returns):.1%}",
        "Profit Factor"     : f"{profit_factor(returns):.3f}",
    }
    return report
