"""
RSI mean reversion strategy adapted from the legacy regime-based strategy folder.
"""
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import rsi, atr


class RSIMeanReversionRegime(Strategy):
    """
    Enter long when RSI crosses above oversold and volume is above its average.
    Enter short when RSI crosses below overbought and volume is above its average.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.rsi_period = self.params.get("rsi_period", 7)
        self.overbought = self.params.get("overbought", 70)
        self.oversold = self.params.get("oversold", 30)
        self.atr_period = self.params.get("atr_period", 14)
        self.atr_multiplier = self.params.get("atr_multiplier", 2.0)
        self.volume_ma_period = self.params.get("volume_ma_period", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["rsi"] = rsi(df["close"], self.rsi_period)
        df["atr"] = atr(df[["high", "low", "close"]], self.atr_period)
        df["volume_ma"] = df["volume"].rolling(self.volume_ma_period).mean()
        df["signal"] = 0

        for idx in range(1, len(df)):
            prev_rsi = df.iloc[idx - 1]["rsi"]
            cur_rsi = df.iloc[idx]["rsi"]
            volume_spike = df.iloc[idx]["volume"] > df.iloc[idx]["volume_ma"]
            if volume_spike and prev_rsi <= self.oversold and cur_rsi > self.oversold:
                df.at[df.index[idx], "signal"] = 1
            elif volume_spike and prev_rsi >= self.overbought and cur_rsi < self.overbought:
                df.at[df.index[idx], "signal"] = -1

        return df[["signal"]]
