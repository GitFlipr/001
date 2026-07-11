"""Extreme Price Drop - Active strategy (Bear). Backtesting adapter."""
import pandas as pd
import numpy as np
from backtesting import Strategy


def _extreme_price_drop_signal(df: pd.DataFrame, drop_threshold: float = 0.05) -> bool:
    """Flash crash: big drop + RSI oversold + bounce + green candle."""
    if len(df) < 50:
        return False
    close = df["Close"] if "Close" in df.columns else df["close"]
    low = df["Low"] if "Low" in df.columns else df["low"]
    drop_1h = (close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] if len(close) > 1 else 0
    if drop_1h > -drop_threshold:
        return False
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    if current_rsi >= 20:
        return False
    recent_low = low.iloc[-10:].min()
    bounce_from_low = (close.iloc[-1] - recent_low) / recent_low if recent_low > 0 else 0
    if bounce_from_low < 0.015:
        return False
    is_green = close.iloc[-1] > close.iloc[-2] if len(close) > 1 else False
    return is_green


class ExtremePriceDropStrategy(Strategy):
    """Extreme Price Drop - flash crash recovery (Bear)."""

    drop_threshold = 0.05

    def init(self):
        pass

    def next(self):
        if len(self.data) < 50:
            return
        df = pd.DataFrame({
            "Open": self.data.Open, "High": self.data.High, "Low": self.data.Low,
            "Close": self.data.Close
        }, index=self.data.index)
        df = df.iloc[: len(self.data)]
        if _extreme_price_drop_signal(df, self.drop_threshold) and not self.position:
            self.buy()
