"""
Momentum Strategy — SMA Crossover with Trend Filter
-----------------------------------------------------
Entry:  Short SMA crosses above Long SMA AND price > Trend SMA
Exit:   Short SMA crosses below Long SMA
Filter: Optional 200-period trend SMA to avoid counter-trend longs
"""

import pandas as pd
from strategies.base_strategy import BaseStrategy


class MomentumStrategy(BaseStrategy):

    def __init__(self, short_window: int = 20, long_window: int = 50,
                 trend_window: int = 200, trend_filter: bool = True):
        super().__init__({
            "short_window" : short_window,
            "long_window"  : long_window,
            "trend_window" : trend_window,
            "trend_filter" : trend_filter,
        })
        self.short_window  = short_window
        self.long_window   = long_window
        self.trend_window  = trend_window
        self.trend_filter  = trend_filter

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["sma_short"] = df["close"].rolling(self.short_window).mean()
        df["sma_long"]  = df["close"].rolling(self.long_window).mean()
        df["sma_trend"] = df["close"].rolling(self.trend_window).mean()

        df["raw_signal"] = 0
        df.loc[df["sma_short"] > df["sma_long"], "raw_signal"] = 1

        if self.trend_filter:
            df.loc[df["close"] < df["sma_trend"], "raw_signal"] = 0

        df["signal"]   = df["raw_signal"]
        df["position"] = df["signal"].shift(1).fillna(0)
        return df.dropna()
