# Crypto Trading Research Platform

A modular, production-style quantitative research and trading analytics platform for cryptocurrency markets. Built for systematic strategy research, live market monitoring, on-chain signal integration, and risk management across CEX derivatives and spot markets.

---

## What This Does

| Module | Description |
|---|---|
| `data/` | Live + historical OHLCV fetcher (Binance, Bybit), funding rate collector, order book snapshot |
| `strategies/` | Pluggable strategy engine: momentum, mean-reversion, funding rate capture |
| `risk/` | Position sizing, drawdown monitor, VaR calculator, regime classifier |
| `onchain/` | Exchange flow tracker, whale alert scanner, liquidation heatmap fetcher |
| `dashboard/` | Terminal dashboard — live P&L, funding rates, on-chain signals, regime state |
| `utils/` | Config loader, logger, performance metrics (Sharpe, Calmar, Sortino) |
| `tests/` | Unit tests for strategy signals, risk engine, and data pipeline |

---

## Architecture

```
crypto-research-platform/
│
├── config.yaml                  # Central config — symbols, thresholds, API keys
│
├── data/
│   ├── market_data.py           # OHLCV fetcher (Binance REST + WebSocket)
│   ├── funding_collector.py     # Multi-exchange funding rate aggregator
│   └── orderbook.py             # Order book snapshot + imbalance calculator
│
├── strategies/
│   ├── base_strategy.py         # Abstract strategy interface
│   ├── momentum.py              # SMA/EMA crossover + trend filter
│   ├── mean_reversion.py        # Z-score based reversion on spread
│   └── funding_carry.py         # Funding rate carry strategy
│
├── risk/
│   ├── position_sizer.py        # Fixed fractional + Kelly criterion sizing
│   ├── drawdown_monitor.py      # Real-time drawdown tracker + circuit breaker
│   ├── var_calculator.py        # Historical + parametric VaR
│   └── regime_classifier.py     # HMM-based market regime detection
│
├── onchain/
│   ├── exchange_flows.py        # Net inflow/outflow via Glassnode API
│   ├── liquidation_scanner.py   # Large liquidation event detector
│   └── whale_tracker.py        # Whale wallet movement monitor
│
├── dashboard/
│   └── terminal_dashboard.py    # Rich-based live terminal UI
│
├── utils/
│   ├── config.py                # Config loader
│   ├── logger.py                # Structured logging
│   └── metrics.py               # Sharpe, Sortino, Calmar, win rate
│
├── backtest.py                  # Full backtest runner with walk-forward validation
├── live_monitor.py              # Live market monitoring entry point
└── tests/
    ├── test_strategies.py
    ├── test_risk.py
    └── test_metrics.py
```

---

## Quickstart

```bash
git clone https://github.com/yourusername/crypto-research-platform
cd crypto-research-platform
pip install -r requirements.txt

# Run a backtest
python backtest.py --strategy momentum --symbol BTCUSDT --interval 4h --days 365

# Launch live terminal dashboard
python live_monitor.py
```

---

## Sample Backtest Output

```
╔══════════════════════════════════════════════════════════╗
║         BACKTEST RESULTS — Momentum Strategy             ║
║         BTCUSDT  |  4h  |  365 days                      ║
╠══════════════════════════════════════════════════════════╣
║  Total Return          +47.3%    (B&H: +41.8%)           ║
║  Sharpe Ratio           1.41                             ║
║  Sortino Ratio          2.03                             ║
║  Calmar Ratio           1.87                             ║
║  Max Drawdown          -14.2%                            ║
║  Win Rate               58.3%                            ║
║  Profit Factor           1.74                            ║
║  Total Trades            87                              ║
║  Avg Trade Duration      2.4 days                        ║
╚══════════════════════════════════════════════════════════╝
Walk-forward validation: 4 folds — avg OOS Sharpe: 1.18
```

---

## Sample Dashboard

```
┌─ LIVE MONITOR ──────────────────── 2025-05-10 09:14:22 UTC ─┐
│                                                               │
│  FUNDING RATES          Binance    Bybit      OKX            │
│  BTCUSDT               +0.0102%  +0.0098%  +0.0115%         │
│  ETHUSDT               +0.0087%  +0.0091%  +0.0083%  ⚠      │
│  SOLUSDT               +0.0201%  +0.0189%  +0.0210%  🔥     │
│                                                               │
│  REGIME  BTC: TRENDING ↑   ETH: RANGING   SOL: HIGH VOL ⚠   │
│                                                               │
│  ON-CHAIN   BTC net flow: -3,241 BTC  ✅ ACCUMULATION        │
│             ETH net flow: +12,440 ETH  ⚠ SELLING PRESSURE    │
│                                                               │
│  STRATEGY SIGNALS                                             │
│  Momentum   BTC: LONG ↑   ETH: FLAT   SOL: LONG ↑           │
│  Carry      BTC: SHORT (funding -ve)                         │
└───────────────────────────────────────────────────────────────┘
```

---

## Requirements

```
requests>=2.31
pandas>=2.0
numpy>=1.24
scipy>=1.11
rich>=13.0
pyyaml>=6.0
websocket-client>=1.6
```

---

## Design Principles

- **Modular:** Every component is independently usable — swap strategies, data sources, or risk models without touching other modules
- **Research-first:** Built for rapid hypothesis testing and clean handoff from research to live execution
- **Production-aware:** Structured logging, config-driven parameters, circuit breakers, and audit trails throughout
- **No magic:** Every signal, metric, and risk calculation is transparent and documented

---

*Built for systematic crypto trading research. Not financial advice.*
