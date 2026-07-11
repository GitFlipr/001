"""SMA ADX Bollinger - Active strategy (Bull). Backtesting adapter."""
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from backtesting import Strategy

_ALLREGIME = Path(__file__).resolve().parents[4] / "New_Dev" / "AllRegime_Master_Bot"
if _ALLREGIME.exists() and str(_ALLREGIME) not in sys.path:
    sys.path.insert(0, str(_ALLREGIME))


def _adx(df: pd.DataFrame, period: int = 14) -> float:
    high = df["High"] if "High" in df.columns else df["high"]
    low = df["Low"] if "Low" in df.columns else df["low"]
    close = df["Close"] if "Close" in df.columns else df["close"]
    plus_dm = high.diff()
    minus_dm = -low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm < 0] = 0
    plus_dm[minus_dm > plus_dm] = 0
    minus_dm[plus_dm > minus_dm] = 0
    tr = pd.concat([high - low, (high - close.shift(1)).abs(), (low - close.shift(1)).abs()], axis=1).max(axis=1)
    atr = tr.rolling(period).mean()
    plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.rolling(period).mean()
    return float(adx.iloc[-1]) if not pd.isna(adx.iloc[-1]) else 0.0


def _sma_adx_bb_signal(df: pd.DataFrame, symbol: str = "") -> str:
    if len(df) < 50:
        return "hold"
    close = df["Close"] if "Close" in df.columns else df["close"]
    volumes = df.get("Volume", df.get("volume"))
    sma = close.rolling(20).mean()
    price_above_sma = close.iloc[-1] > sma.iloc[-1]
    adx = _adx(df)
    adx_min = 22 if symbol in {"SOL", "INJ", "SUI", "ETH", "ONDO", "XLM"} else 30
    adx_strong = adx > adx_min
    volume_confirmed = True
    if volumes is not None and len(volumes) >= 20:
        vol_ma = volumes.rolling(20).mean().iloc[-1]
        vol_mult = 1.05 if symbol in {"SOL", "INJ", "SUI", "ETH", "ONDO", "XLM"} else 1.1
        volume_confirmed = volumes.iloc[-1] >= vol_ma * vol_mult
    std = close.rolling(20).std()
    lower_band = sma - (std * 2.0)
    band_mult = 1.05 if symbol in {"SOL", "INJ", "SUI", "ETH", "ONDO", "XLM"} else 1.02
    price_near_lower = close.iloc[-1] <= lower_band.iloc[-1] * band_mult
    conditions = (price_above_sma, adx_strong, price_near_lower, volume_confirmed)
    if symbol in {"SOL", "INJ", "SUI", "ETH", "ONDO", "XLM"}:
        if sum(conditions) >= 2:
            return "buy"
    elif all(conditions):
        return "buy"
    return "hold"


class SmaAdxBollingerStrategy(Strategy):
    """SMA + ADX + Bollinger - Bull strategy."""

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
        if _sma_adx_bb_signal(df) == "buy" and not self.position:
            self.buy()
