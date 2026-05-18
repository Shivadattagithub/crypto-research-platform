"""
Market Data Fetcher
--------------------
Fetches OHLCV candles and ticker data from Binance REST API.
Supports multiple symbols and timeframes with rate-limit handling.
"""

import requests
import pandas as pd
import time
from datetime import datetime, timedelta


BINANCE_BASE = "https://api.binance.com"


def fetch_ohlcv(symbol: str, interval: str = "4h", days: int = 365) -> pd.DataFrame:
    """
    Fetch OHLCV candles from Binance. Handles pagination for long lookbacks.
    
    Args:
        symbol:   Trading pair e.g. "BTCUSDT"
        interval: Candle size: 1m, 5m, 15m, 1h, 4h, 1d
        days:     Number of calendar days to fetch

    Returns:
        DataFrame with columns: open, high, low, close, volume
        Indexed by UTC datetime.
    """
    limit      = 1000  # Binance max per request
    since_ms   = int((datetime.utcnow() - timedelta(days=days)).timestamp() * 1000)
    all_candles = []

    while True:
        url    = f"{BINANCE_BASE}/api/v3/klines"
        params = {
            "symbol"    : symbol,
            "interval"  : interval,
            "startTime" : since_ms,
            "limit"     : limit,
        }
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        candles = r.json()

        if not candles:
            break

        all_candles.extend(candles)

        if len(candles) < limit:
            break

        since_ms = candles[-1][0] + 1
        time.sleep(0.1)  # Respect rate limits

    if not all_candles:
        return pd.DataFrame()

    cols = ["open_time","open","high","low","close","volume",
            "close_time","quote_vol","trades","taker_base","taker_quote","ignore"]
    df = pd.DataFrame(all_candles, columns=cols)
    df["open_time"] = pd.to_datetime(df["open_time"], unit="ms", utc=True)
    df.set_index("open_time", inplace=True)

    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = df[col].astype(float)

    return df[["open", "high", "low", "close", "volume"]]


def fetch_multi(symbols: list, interval: str = "4h", days: int = 365) -> dict:
    """Fetch OHLCV for multiple symbols. Returns dict of DataFrames."""
    result = {}
    for sym in symbols:
        print(f"  Fetching {sym}...")
        try:
            result[sym] = fetch_ohlcv(sym, interval, days)
        except Exception as e:
            print(f"  Warning: failed to fetch {sym}: {e}")
    return result


def fetch_ticker(symbol: str) -> dict:
    """Fetch current 24h ticker stats for a symbol."""
    url = f"{BINANCE_BASE}/api/v3/ticker/24hr"
    r   = requests.get(url, params={"symbol": symbol}, timeout=5)
    r.raise_for_status()
    t = r.json()
    return {
        "symbol"        : t["symbol"],
        "last_price"    : float(t["lastPrice"]),
        "price_change"  : float(t["priceChangePercent"]),
        "volume_24h"    : float(t["quoteVolume"]),
        "high_24h"      : float(t["highPrice"]),
        "low_24h"       : float(t["lowPrice"]),
    }
