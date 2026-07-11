"""Candlestick Pattern - Active strategy (Chemical_X). Engulfing + Hammer."""
import sys
from pathlib import Path
import pandas as pd
from backtesting import Strategy

_ALLREGIME = Path(__file__).resolve().parents[4] / "New_Dev" / "AllRegime_Master_Bot"
if _ALLREGIME.exists() and str(_ALLREGIME) not in sys.path:
    sys.path.insert(0, str(_ALLREGIME))


def _volume_confirmed(df: pd.DataFrame, mult: float = 1.2, window: int = 20) -> bool:
    vol = df.get("Volume", df.get("volume"))
    if vol is None or len(vol) < window:
        return True
    avg = vol.rolling(window).mean().iloc[-1]
    cur = vol.iloc[-1]
    return pd.isna(avg) or pd.isna(cur) or cur >= avg * mult


def _engulfing(df: pd.DataFrame) -> str:
    if len(df) < 2:
        return ""
    prev, curr = df.iloc[-2], df.iloc[-1]
    po, pc = prev["Open"], prev["Close"]
    co, cc = curr["Open"], curr["Close"]
    if prev["Close"] < prev["Open"] and curr["Close"] > curr["Open"] and curr["Open"] < prev["Close"] and curr["Close"] > prev["Open"]:
        return "buy"
    if prev["Close"] > prev["Open"] and curr["Close"] < curr["Open"] and curr["Open"] > prev["Close"] and curr["Close"] < prev["Open"]:
        return "sell"
    return ""


def _hammer(df: pd.DataFrame) -> str:
    if len(df) < 1:
        return ""
    c = df.iloc[-1]
    o, h, l_, cl = c["Open"], c["High"], c["Low"], c["Close"]
    body = abs(cl - o)
    total = h - l_
    if total <= 0:
        return ""
    lower_wick = min(o, cl) - l_
    upper_wick = h - max(o, cl)
    if body > 0 and lower_wick >= 2 * body and upper_wick <= 0.1 * body and cl > o:
        return "buy"
    if body > 0 and lower_wick >= 2 * body and upper_wick <= 0.1 * body and cl < o:
        return "sell"
    return ""


def _trend_ok(df: pd.DataFrame) -> bool:
    if "Close" not in df.columns or len(df) < 10:
        return True
    close = df["Close"]
    sma10 = close.rolling(10).mean().iloc[-1]
    sma20 = close.rolling(min(20, len(df))).mean().iloc[-1] if len(df) >= 20 else sma10
    return close.iloc[-1] > sma10 and sma10 >= sma20


def _candlestick_signal(df: pd.DataFrame) -> str:
    if len(df) < 10 or not _volume_confirmed(df, 1.5):
        return "hold"
    buy_score = 0
    sell_score = 0
    if _engulfing(df) == "buy":
        buy_score += 1.0
    elif _engulfing(df) == "sell":
        sell_score += 1.0
    if _hammer(df) == "buy":
        buy_score += 0.9
    elif _hammer(df) == "sell":
        sell_score += 0.9
    if buy_score >= 0.9 and _trend_ok(df):
        return "buy"
    if sell_score >= 0.9:
        return "sell"
    return "hold"


class CandlestickPatternStrategy(Strategy):
    """Candlestick Pattern - engulfing + hammer (Chemical_X)."""

    def init(self):
        pass

    def next(self):
        if len(self.data) < 10:
            return
        df = pd.DataFrame({
            "Open": self.data.Open, "High": self.data.High, "Low": self.data.Low,
            "Close": self.data.Close, "Volume": self.data.Volume
        }, index=self.data.index)
        df = df.iloc[: len(self.data)]
        signal = _candlestick_signal(df)
        if signal == "buy" and not self.position:
            self.buy()
        elif signal == "sell" and self.position:
            self.position.close()
