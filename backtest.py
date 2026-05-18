"""
Backtest Runner
----------------
Runs a full backtest with walk-forward validation.
Supports momentum and mean-reversion strategies.

Usage:
    python backtest.py --strategy momentum --symbol BTCUSDT --interval 4h --days 365
    python backtest.py --strategy mean_reversion --symbol ETHUSDT --days 180
"""

import argparse
import pandas as pd
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from data.market_data import fetch_ohlcv
from strategies.momentum import MomentumStrategy
from strategies.mean_reversion import MeanReversionStrategy
from risk.drawdown_monitor import DrawdownMonitor
from utils.metrics import full_report, sharpe_ratio

INITIAL_CAPITAL = 10_000.0
TAKER_FEE       = 0.0006


def run_backtest(df: pd.DataFrame, strategy) -> pd.DataFrame:
    """Core backtest loop — applies strategy signals to price data."""
    df = strategy.generate_signals(df)

    df["bar_return"]      = df["close"].pct_change().fillna(0)
    df["trade"]           = df["position"].diff().abs()
    df["cost"]            = df["trade"] * TAKER_FEE
    df["strategy_return"] = df["position"] * df["bar_return"] - df["cost"]
    df["equity"]          = INITIAL_CAPITAL * (1 + df["strategy_return"]).cumprod()
    df["bnh_equity"]      = INITIAL_CAPITAL * (1 + df["bar_return"]).cumprod()
    return df


def walk_forward(df: pd.DataFrame, strategy, n_folds: int = 4) -> list:
    """
    Walk-forward validation — splits data into n_folds.
    Trains on 70% of each fold, tests on remaining 30%.
    Returns list of out-of-sample Sharpe ratios.
    """
    fold_size  = len(df) // n_folds
    oos_sharpes = []

    for i in range(n_folds):
        start      = i * fold_size
        end        = start + fold_size
        fold_data  = df.iloc[start:end].copy()

        train_end  = int(len(fold_data) * 0.7)
        test_data  = fold_data.iloc[train_end:].copy()

        if len(test_data) < 30:
            continue

        result = run_backtest(test_data, strategy)
        sr     = sharpe_ratio(result["strategy_return"])
        oos_sharpes.append(sr)
        print(f"  Fold {i+1}/{n_folds}  OOS Sharpe: {sr:.3f}  "
              f"OOS bars: {len(test_data)}")

    return oos_sharpes


def print_results(symbol: str, interval: str, df: pd.DataFrame,
                  metrics: dict, oos_sharpes: list):
    """Pretty-print backtest results to terminal."""
    width = 58
    print("\n" + "=" * width)
    print(f"  BACKTEST RESULTS — {df['position'].iloc[-1] and 'LONG' or 'FLAT'} at close")
    print(f"  {symbol}  |  {interval}  |  {len(df)} bars")
    print(f"  {df.index[0].date()} → {df.index[-1].date()}")
    print("=" * width)
    for k, v in metrics.items():
        print(f"  {k:<24} {v:>12}")
    print("  " + "-" * (width - 2))
    bnh = (df["bnh_equity"].iloc[-1] / INITIAL_CAPITAL - 1)
    print(f"  {'Buy & Hold Return':<24} {bnh:>+12.2%}")
    print("=" * width)

    if oos_sharpes:
        avg_oos = np.mean(oos_sharpes)
        print(f"\n  Walk-forward ({len(oos_sharpes)} folds)")
        print(f"  Avg OOS Sharpe: {avg_oos:.3f}  |  "
              f"Min: {min(oos_sharpes):.3f}  Max: {max(oos_sharpes):.3f}")
    print()


def main():
    parser = argparse.ArgumentParser(description="Crypto Backtest Runner")
    parser.add_argument("--strategy", default="momentum",
                        choices=["momentum", "mean_reversion"])
    parser.add_argument("--symbol",   default="BTCUSDT")
    parser.add_argument("--interval", default="4h")
    parser.add_argument("--days",     type=int, default=365)
    parser.add_argument("--folds",    type=int, default=4)
    args = parser.parse_args()

    print(f"\nFetching {args.days} days of {args.interval} data for {args.symbol}...")
    df = fetch_ohlcv(args.symbol, args.interval, args.days)

    if df.empty:
        print("No data returned. Check symbol and interval.")
        return

    print(f"Fetched {len(df)} bars. Running {args.strategy} strategy...\n")

    if args.strategy == "momentum":
        strategy = MomentumStrategy(short_window=20, long_window=50,
                                    trend_window=200, trend_filter=True)
    else:
        strategy = MeanReversionStrategy(window=30, entry_threshold=2.0,
                                         exit_threshold=0.5)

    result  = run_backtest(df, strategy)
    metrics = full_report(result["strategy_return"], result["position"])

    print(f"Running walk-forward validation ({args.folds} folds)...")
    oos = walk_forward(df, strategy, n_folds=args.folds)

    print_results(args.symbol, args.interval, result, metrics, oos)


if __name__ == "__main__":
    main()
