"""
Drawdown Monitor & Circuit Breaker
------------------------------------
Tracks real-time drawdown from equity peak.
Triggers a circuit breaker if drawdown exceeds a defined threshold.
"""

import pandas as pd


class DrawdownMonitor:

    def __init__(self, max_drawdown: float = 0.15):
        """
        Args:
            max_drawdown: Circuit breaker threshold as fraction (e.g. 0.15 = 15%)
        """
        self.max_drawdown  = max_drawdown
        self.peak_equity   = None
        self.halted        = False

    def update(self, current_equity: float) -> dict:
        """
        Update monitor with latest equity value.
        Returns status dict with current drawdown and halt flag.
        """
        if self.peak_equity is None or current_equity > self.peak_equity:
            self.peak_equity = current_equity

        drawdown = (current_equity - self.peak_equity) / self.peak_equity

        if drawdown <= -self.max_drawdown:
            self.halted = True

        return {
            "current_equity" : current_equity,
            "peak_equity"    : self.peak_equity,
            "drawdown"       : drawdown,
            "halted"         : self.halted,
        }

    def reset(self):
        """Manually reset circuit breaker (requires human review)."""
        self.halted      = False
        self.peak_equity = None

    @staticmethod
    def from_equity_series(equity: pd.Series) -> pd.DataFrame:
        """Compute full drawdown series from an equity curve."""
        rolling_max = equity.cummax()
        drawdown    = (equity - rolling_max) / rolling_max
        return pd.DataFrame({
            "equity"      : equity,
            "peak"        : rolling_max,
            "drawdown"    : drawdown,
        })
