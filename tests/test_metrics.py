"""
Unit Tests — Performance Metrics
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
import unittest
from utils.metrics import (sharpe_ratio, sortino_ratio, max_drawdown,
                            win_rate, profit_factor, annualised_return)


class TestMetrics(unittest.TestCase):

    def setUp(self):
        np.random.seed(42)
        self.pos_returns  = pd.Series(np.random.normal(0.001, 0.02, 365))
        self.neg_returns  = pd.Series(np.random.normal(-0.001, 0.02, 365))
        self.zero_returns = pd.Series(np.zeros(100))

    def test_sharpe_positive_mean(self):
        sr = sharpe_ratio(self.pos_returns)
        self.assertGreater(sr, 0)

    def test_sharpe_zero_std(self):
        sr = sharpe_ratio(self.zero_returns)
        self.assertEqual(sr, 0.0)

    def test_sortino_gte_sharpe_for_positive(self):
        sr  = sharpe_ratio(self.pos_returns)
        sor = sortino_ratio(self.pos_returns)
        self.assertGreaterEqual(sor, sr)

    def test_max_drawdown_negative(self):
        mdd = max_drawdown(self.neg_returns)
        self.assertLess(mdd, 0)

    def test_max_drawdown_always_positive_returns(self):
        always_up = pd.Series([0.01] * 100)
        mdd = max_drawdown(always_up)
        self.assertAlmostEqual(mdd, 0.0, places=5)

    def test_win_rate_range(self):
        wr = win_rate(self.pos_returns)
        self.assertGreaterEqual(wr, 0.0)
        self.assertLessEqual(wr, 1.0)

    def test_profit_factor_positive(self):
        pf = profit_factor(self.pos_returns)
        self.assertGreater(pf, 0)

    def test_annualised_return(self):
        flat = pd.Series([0.0] * 365)
        self.assertAlmostEqual(annualised_return(flat), 0.0, places=5)


if __name__ == "__main__":
    unittest.main()
