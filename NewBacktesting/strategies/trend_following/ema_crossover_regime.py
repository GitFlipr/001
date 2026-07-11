"""
EMA crossover strategy adapted from the legacy regime-based strategy folder.
"""
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema


class EMACrossoverRegime(Strategy):
    """
    Simple regime-friendly EMA crossover wrapper.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.short_window = self.params.get("short_window", 9)
        self.long_window = self.params.get("long_window", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["ema_short"] = ema(df["close"], self.short_window)
        df["ema_long"] = ema(df["close"], self.long_window)
        df["signal"] = 0
        df.loc[df["ema_short"] > df["ema_long"], "signal"] = 1
        df.loc[df["ema_short"] < df["ema_long"], "signal"] = -1
        return df[["signal"]]
