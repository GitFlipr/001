"""
ROC momentum strategy migrated from the legacy backup set.
"""
import pandas as pd
import numpy as np

from backtest.strategies.base import Strategy
from backtest.utils.indicators import roc, atr


class ROCMomentum(Strategy):
    """
    Go long when ROC is positive and volatility is below a threshold.
    Go short when ROC is negative and volatility is below a threshold.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.roc_period = self.params.get("roc_period", 60)
        self.atr_period = self.params.get("atr_period", 14)
        self.atr_max_pct = self.params.get("atr_max_pct", 0.05)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["roc"] = roc(df["close"], self.roc_period)
        atr_series = atr(df[["high", "low", "close"]], self.atr_period)
        df["atr"] = atr_series
        df["signal"] = 0

        for idx in range(len(df)):
            if idx < self.roc_period + 2:
                continue
            close = df.iloc[idx]["close"]
            vol_pct = df.iloc[idx]["atr"] / close if close else np.inf
            if vol_pct > self.atr_max_pct:
                continue
            if df.iloc[idx]["roc"] > 0:
                df.at[df.index[idx], "signal"] = 1
            elif df.iloc[idx]["roc"] < 0:
                df.at[df.index[idx], "signal"] = -1

        return df[["signal"]]
