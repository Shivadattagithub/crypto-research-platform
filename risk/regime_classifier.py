"""
Market Regime Classifier
--------------------------
Classifies market regime using volatility, trend strength,
and price momentum. Three regimes: TRENDING, RANGING, HIGH_VOLATILITY.

Uses rule-based classification (no ML dependency) for transparency
and easy auditability in a trading context.
"""

import pandas as pd
import numpy as np


REGIMES = {
    "TRENDING"       : "trending",
    "RANGING"        : "ranging",
    "HIGH_VOLATILITY": "high_vol",
}


def classify_regime(df: pd.DataFrame,
                    vol_window: int   = 20,
                    trend_window: int = 50,
                    high_vol_mult: float = 2.0) -> pd.DataFrame:
    """
    Classify each bar into a market regime.

    Logic:
      - HIGH_VOLATILITY : rolling vol > 2x its own 100-day average
      - TRENDING        : ADX-proxy (slope of SMA) above threshold
      - RANGING         : everything else
    """
    df = df.copy()

    # Rolling volatility (annualised)
    df["returns"]    = df["close"].pct_change()
    df["vol"]        = df["returns"].rolling(vol_window).std() * np.sqrt(365)
    df["vol_ma"]     = df["vol"].rolling(100).mean()

    # Trend proxy: normalised slope of SMA
    df["sma"]        = df["close"].rolling(trend_window).mean()
    df["sma_slope"]  = df["sma"].pct_change(5)  # 5-bar slope

    def assign(row):
        if pd.isna(row["vol"]) or pd.isna(row["vol_ma"]):
            return "unknown"
        if row["vol"] > row["vol_ma"] * high_vol_mult:
            return REGIMES["HIGH_VOLATILITY"]
        if abs(row["sma_slope"]) > 0.01:  # >1% slope over 5 bars
            return REGIMES["TRENDING"]
        return REGIMES["RANGING"]

    df["regime"] = df.apply(assign, axis=1)
    return df
