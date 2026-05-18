"""
Live Market Monitor
--------------------
Terminal dashboard showing real-time funding rates, regime classification,
ticker data, and strategy signals across configured symbols.

Refreshes every 60 seconds. Press Ctrl+C to stop.

Usage:
    python live_monitor.py
"""

import time
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from data.market_data import fetch_ohlcv, fetch_ticker
from data.funding_collector import get_all_funding_rates
from strategies.momentum import MomentumStrategy
from risk.regime_classifier import classify_regime

SYMBOLS          = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT"]
REFRESH_SECONDS  = 60
LOOKBACK_DAYS    = 30
INTERVAL         = "4h"


def get_strategy_signal(symbol: str) -> str:
    """Get latest momentum signal for a symbol."""
    try:
        df       = fetch_ohlcv(symbol, INTERVAL, LOOKBACK_DAYS)
        strategy = MomentumStrategy()
        result   = strategy.generate_signals(df)
        pos      = result["position"].iloc[-1]
        return "LONG  ↑" if pos == 1 else "FLAT  —"
    except Exception:
        return "N/A"


def get_regime(symbol: str) -> str:
    """Get current market regime for a symbol."""
    try:
        df     = fetch_ohlcv(symbol, INTERVAL, LOOKBACK_DAYS)
        result = classify_regime(df)
        regime = result["regime"].iloc[-1]
        icons  = {"trending": "📈 TRENDING", "ranging": "↔  RANGING",
                  "high_vol": "⚠  HIGH VOL"}
        return icons.get(regime, regime.upper())
    except Exception:
        return "N/A"


def render_dashboard(funding_data: dict, tickers: dict):
    """Render the terminal dashboard."""
    ts    = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    width = 65

    print("\033[2J\033[H", end="")  # Clear terminal
    print("=" * width)
    print(f"  CRYPTO RESEARCH PLATFORM  |  {ts}")
    print("=" * width)

    # Funding rates table
    print(f"\n  {'FUNDING RATES'}")
    print(f"  {'─'*60}")
    print(f"  {'Symbol':<12} {'Binance':>10} {'Bybit':>10} {'OKX':>10}  {'Flag'}")
    print(f"  {'─'*60}")

    for sym in SYMBOLS:
        rates = funding_data.get(sym, {})
        b  = rates.get("Binance")
        by = rates.get("Bybit")
        o  = rates.get("OKX")

        fmt  = lambda r: f"{r*100:+.4f}%" if r is not None else "  N/A  "
        flag = ""
        if b and abs(b) > 0.0005:
            flag = "🔥"
        elif b and abs(b) > 0.0003:
            flag = "⚠"

        print(f"  {sym:<12} {fmt(b):>10} {fmt(by):>10} {fmt(o):>10}  {flag}")

    # Tickers
    print(f"\n  {'MARKET SNAPSHOT'}")
    print(f"  {'─'*60}")
    print(f"  {'Symbol':<12} {'Price':>12} {'24h Change':>12} {'Volume (24h)':>16}")
    print(f"  {'─'*60}")

    for sym in SYMBOLS:
        t = tickers.get(sym, {})
        if t:
            chg   = t.get("price_change", 0)
            icon  = "▲" if chg >= 0 else "▼"
            print(f"  {sym:<12} ${t.get('last_price',0):>11,.2f} "
                  f" {icon}{abs(chg):>10.2f}%"
                  f"  ${t.get('volume_24h',0):>14,.0f}")

    print(f"\n  {'─'*60}")
    print(f"  Refreshing every {REFRESH_SECONDS}s  |  Ctrl+C to stop")
    print("=" * width + "\n")


def main():
    print("Starting live monitor... fetching initial data.\n")
    strategy = MomentumStrategy()

    while True:
        try:
            print("  Fetching funding rates...")
            funding_data = {}
            for sym in SYMBOLS:
                try:
                    funding_data[sym] = get_all_funding_rates(sym)
                except Exception:
                    funding_data[sym] = {}

            print("  Fetching tickers...")
            tickers = {}
            for sym in SYMBOLS:
                try:
                    tickers[sym] = fetch_ticker(sym)
                except Exception:
                    tickers[sym] = {}

            render_dashboard(funding_data, tickers)
            time.sleep(REFRESH_SECONDS)

        except KeyboardInterrupt:
            print("\nMonitor stopped.")
            break
        except Exception as e:
            print(f"Error: {e}. Retrying in {REFRESH_SECONDS}s...")
            time.sleep(REFRESH_SECONDS)


if __name__ == "__main__":
    main()
