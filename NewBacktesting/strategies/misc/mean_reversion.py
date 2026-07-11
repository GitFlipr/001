"""
Generic mean reversion wrapper for the new package.
"""
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import rsi


class MeanReversion(Strategy):
    """
    Simple mean-reversion signal based on RSI oversold/overbought thresholds.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.rsi_period = self.params.get("rsi_period", 14)
        self.oversold = self.params.get("oversold", 30)
        self.overbought = self.params.get("overbought", 70)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["rsi"] = rsi(df["close"], self.rsi_period)
        df["signal"] = 0
        df.loc[df["rsi"] < self.oversold, "signal"] = 1
        df.loc[df["rsi"] > self.overbought, "signal"] = -1
        return df[["signal"]]
