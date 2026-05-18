"""
Multi-Exchange Funding Rate Collector
---------------------------------------
Fetches real-time perpetual funding rates from Binance, Bybit, and OKX.
"""

import requests


def get_binance_funding(symbol: str) -> float | None:
    try:
        r = requests.get("https://fapi.binance.com/fapi/v1/premiumIndex",
                         params={"symbol": symbol}, timeout=5)
        r.raise_for_status()
        return float(r.json()["lastFundingRate"])
    except Exception:
        return None


def get_bybit_funding(symbol: str) -> float | None:
    try:
        r = requests.get("https://api.bybit.com/v5/market/tickers",
                         params={"category": "linear", "symbol": symbol}, timeout=5)
        r.raise_for_status()
        items = r.json().get("result", {}).get("list", [])
        return float(items[0]["fundingRate"]) if items else None
    except Exception:
        return None


def get_okx_funding(symbol: str) -> float | None:
    base    = symbol.replace("USDT", "")
    inst_id = f"{base}-USDT-SWAP"
    try:
        r = requests.get("https://www.okx.com/api/v5/public/funding-rate",
                         params={"instId": inst_id}, timeout=5)
        r.raise_for_status()
        data = r.json().get("data", [])
        return float(data[0]["fundingRate"]) if data else None
    except Exception:
        return None


def get_all_funding_rates(symbol: str) -> dict:
    """Return funding rates from all three exchanges for a symbol."""
    return {
        "Binance" : get_binance_funding(symbol),
        "Bybit"   : get_bybit_funding(symbol),
        "OKX"     : get_okx_funding(symbol),
    }
