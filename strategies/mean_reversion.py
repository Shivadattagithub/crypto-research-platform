"""
Mean Reversion Strategy — Z-Score on Rolling Spread
-----------------------------------------------------
Entry:  Z-score of price vs rolling mean falls below -entry_threshold (oversold)
Exit:   Z-score crosses back above exit_threshold
Uses rolling z-score to avoid lookahead bias.
"""

import pandas as pd
import numpy as np
from strategies.base_strategy import BaseStrategy


class MeanReversionStrategy(BaseStrategy):

    def __init__(self, window: int = 30, entry_threshold: float = 2.0,
                 exit_threshold: float = 0.5):
        super().__init__({
            "window"           : window,
            "entry_threshold"  : entry_threshold,
            "exit_threshold"   : exit_threshold,
        })
        self.window           = window
        self.entry_threshold  = entry_threshold
        self.exit_threshold   = exit_threshold

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        roll_mean   = df["close"].rolling(self.window).mean()
        roll_std    = df["close"].rolling(self.window).std()
        df["zscore"] = (df["close"] - roll_mean) / roll_std

        signal   = pd.Series(0, index=df.index)
        position = 0

        for i in range(len(df)):
            z = df["zscore"].iloc[i]
            if position == 0 and z < -self.entry_threshold:
                position = 1   # Enter long — price is cheap
            elif position == 1 and z > self.exit_threshold:
                position = 0   # Exit
            signal.iloc[i] = position

        df["signal"]   = signal
        df["position"] = signal.shift(1).fillna(0)
        return df.dropna()
