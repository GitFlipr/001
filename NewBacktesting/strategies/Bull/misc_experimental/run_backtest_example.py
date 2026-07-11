#!/usr/bin/env python3
"""
Run a quick backtest for one of the new strategies (requires: backtesting, pandas, talib).

  pip install backtesting pandas ta-lib  # or use pip install TA-Lib with binary wheel

Example:
  python run_backtest_example.py --csv "C:/path/to/BTC_1d.csv" --strategy btc_trend

CSV columns: Open, High, Low, Close, Volume (Date index optional).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
from backtesting import Backtest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

STRATEGIES = {
    "dual_filter": ("conservative.dual_filter_trend", "DualFilterTrendStrategy"),
    "swing_pullback": ("swing.slow_trend_pullback", "SlowTrendPullbackStrategy"),
    "rsi_burst": ("quick.rsi_burst_scalp", "RsiBurstScalpStrategy"),
    "multi_vote": ("systematic.multi_signal_vote", "MultiSignalVoteStrategy"),
    "btc_trend": ("btc.btc_regime_trend", "BtcRegimeTrendStrategy"),
    "xrp_breakout": ("xrp.xrp_vol_breakout", "XrpVolBreakoutStrategy"),
    "bull_stack": ("bull_run.stacked_ema_parabolic", "StackedEmaParabolicStrategy"),
    "donchian": ("trending.donchian_breakout", "DonchianBreakoutStrategy"),
}


def load_ohlcv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=True, index_col=0)
    # normalize columns
    colmap = {c: c.capitalize() for c in df.columns if c.lower() in ("open", "high", "low", "close", "volume")}
    df = df.rename(columns=colmap)
    for need in ("Open", "High", "Low", "Close", "Volume"):
        if need not in df.columns:
            raise SystemExit(f"CSV missing column {need}; got {list(df.columns)}")
    return df


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, required=True, help="OHLCV CSV")
    ap.add_argument("--strategy", choices=sorted(STRATEGIES.keys()), default="donchian")
    ap.add_argument("--cash", type=float, default=100_000)
    ap.add_argument("--commission", type=float, default=0.0006)
    args = ap.parse_args()

    mod_name, cls_name = STRATEGIES[args.strategy]
    import importlib

    mod = importlib.import_module(mod_name)
    strat_cls = getattr(mod, cls_name)
    df = load_ohlcv(args.csv)
    bt = Backtest(df, strat_cls, cash=args.cash, commission=args.commission)
    stats = bt.run()
    print(stats)
    return 0
