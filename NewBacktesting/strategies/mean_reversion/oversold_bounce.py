"""Oversold Bounce - Active strategy (Bear). Backtesting adapter."""
import pandas as pd
import numpy as np
from backtesting import Strategy


def _oversold_bounce_signal(df: pd.DataFrame) -> bool:
    """RSI < 30 and price at/near lower Bollinger Band."""
    if len(df) < 50:
        return False
    close = df["Close"] if "Close" in df.columns else df["close"]
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1]
    if pd.isna(current_rsi):
        return False
    bb_middle = close.rolling(20).mean().iloc[-1]
    bb_std = close.rolling(20).std().iloc[-1]
    bb_lower = bb_middle - (2 * bb_std)
    current_price = close.iloc[-1]
    return current_rsi < 30 and current_price <= bb_lower * 1.02


class OversoldBounceStrategy(Strategy):
    """Oversold Bounce - Bear market relief bounces."""

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
        if _oversold_bounce_signal(df) and not self.position:
            self.buy()
