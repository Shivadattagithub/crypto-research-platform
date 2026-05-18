"""
Base Strategy Interface
------------------------
All strategies inherit from BaseStrategy and implement generate_signals().
This enforces a consistent interface across the strategy library.
"""

from abc import ABC, abstractmethod
import pandas as pd


class BaseStrategy(ABC):
    """Abstract base class for all trading strategies."""

    def __init__(self, params: dict):
        self.params = params
        self.name   = self.__class__.__name__

    @abstractmethod
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Given OHLCV data, return a DataFrame with a 'signal' column:
          +1 = long
           0 = flat
          -1 = short (where applicable)
        """
        pass

    def __repr__(self):
        return f"{self.name}({self.params})"
