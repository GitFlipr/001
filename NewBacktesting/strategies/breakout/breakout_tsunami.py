"""Breakout Tsunami - Active strategy (Bull, AltAssets). Backtesting adapter."""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from backtesting import Strategy

# Add AllRegime for shared candlestick_patterns if needed
_ALLREGIME = Path(__file__).resolve().parents[4] / "New_Dev" / "AllRegime_Master_Bot"
if _ALLREGIME.exists() and str(_ALLREGIME) not in sys.path:
    sys.path.insert(0, str(_ALLREGIME))


def _breakout_signal(df: pd.DataFrame) -> str:
    """Breakout Tsunami logic: resistance breakouts with volume."""
    if len(df) < 10:
        return "hold"
    high = df["High"] if "High" in df.columns else df["high"]
    close = df["Close"] if "Close" in df.columns else df["close"]
    volume = df.get("Volume", df.get("volume", pd.Series(1.0, index=df.index)))
    if not isinstance(volume, pd.Series):
        volume = pd.Series(1.0, index=df.index)

    resistance_3 = high.iloc[-3:-1].max()
    resistance_5 = high.iloc[-5:-1].max()
    resistance_10 = high.iloc[-10:-1].max()
    breakout_3 = close.iloc[-1] > resistance_3
    breakout_5 = close.iloc[-1] > resistance_5
    breakout_10 = close.iloc[-1] > resistance_10
    above_ma3 = close.iloc[-1] > close.iloc[-3:].mean()
    above_ma5 = close.iloc[-1] > close.iloc[-5:].mean()
    volume_up = len(volume) > 2 and volume.iloc[-1] > volume.iloc[-2]
    tsunami_breakout = breakout_3 or breakout_5 or breakout_10 or above_ma3 or above_ma5 or volume_up

    # Confirmation: above SMA20
    sma20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else close.iloc[-5:].mean()
    above_sma = close.iloc[-1] > sma20

    if tsunami_breakout and above_sma and not np.isnan(sma20):
        return "buy"
    if close.iloc[-1] < close.iloc[-5:].mean() * 0.93:
        return "sell"
    return "hold"


class BreakoutTsunamiStrategy(Strategy):
    """Breakout Tsunami - resistance breakouts with trend confirmation."""

    def init(self):
        pass

    def next(self):
        if len(self.data) < 20:
            return
        df = pd.DataFrame({
            "Open": self.data.Open, "High": self.data.High, "Low": self.data.Low,
            "Close": self.data.Close, "Volume": self.data.Volume
        }, index=self.data.index)
        df = df.iloc[: len(self.data)]
        signal = _breakout_signal(df)
        if signal == "buy" and not self.position:
            self.buy()
        elif signal == "sell" and self.position:
            self.position.close()
