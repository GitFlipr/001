"""Black Swan - Active strategy (Bull). Backtesting adapter."""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from backtesting import Strategy

_ALLREGIME = Path(__file__).resolve().parents[4] / "New_Dev" / "AllRegime_Master_Bot"
if _ALLREGIME.exists() and str(_ALLREGIME) not in sys.path:
    sys.path.insert(0, str(_ALLREGIME))


def _black_swan_signal(df: pd.DataFrame) -> str:
    """Black Swan: volatility spike + volume surge + momentum."""
    if df is None or len(df) < 50:
        return "hold"
    close = df["Close"] if "Close" in df.columns else df["close"]
    high = df["High"] if "High" in df.columns else df["high"]
    low = df["Low"] if "Low" in df.columns else df["low"]
    volume = df["Volume"] if "Volume" in df.columns else df["volume"]

    # ATR
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    atr = tr.rolling(14).mean()
    avg_atr = atr.iloc[-50:].mean()
    current_atr = atr.iloc[-1]
    if pd.isna(avg_atr) or avg_atr <= 0:
        return "hold"
    if current_atr / avg_atr >= 2.0:
        return "hold"  # already extreme
    vol_spike = current_atr / avg_atr >= 1.20
    vol_ma = volume.rolling(20).mean().iloc[-1]
    vol_surge = vol_ma > 0 and volume.iloc[-1] >= vol_ma * 1.5
    mom_5 = (close.iloc[-1] - close.iloc[-6]) / close.iloc[-6] if len(close) >= 6 else 0
    mom_10 = (close.iloc[-1] - close.iloc[-11]) / close.iloc[-11] if len(close) >= 11 else 0
    mom_20 = (close.iloc[-1] - close.iloc[-21]) / close.iloc[-21] if len(close) >= 21 else 0
    momentum_ok = sum(1 for m in [mom_5, mom_10, mom_20] if m >= 0.003) >= 2
    if vol_spike and vol_surge and momentum_ok:
        return "buy"
    return "hold"


class BlackSwanStrategy(Strategy):
    """Black Swan - volatility expansion + volume surge + momentum."""

    def init(self):
        pass

    def next(self):
        if len(self.data) < 50:
            return
        df = pd.DataFrame({
            "Open": self.data.Open, "High": self.data.High, "Low": self.data.Low,
            "Close": self.data.Close, "Volume": self.data.Volume
        }, index=self.data.index)
        df = df.iloc[: len(self.data)]
        if _black_swan_signal(df) == "buy" and not self.position:
            self.buy()
