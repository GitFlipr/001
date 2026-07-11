"""
EMA Ultimate Oscillator strategy adapted from the legacy backtesting harness.
"""
import pandas as pd
import numpy as np

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, atr


class EMAUltimateOscillator(Strategy):
    """
    A simple oscillator-style trend strategy using EMA crossover plus ATR-based exits.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.ema_window = self.params.get("ema_window", 20)
        self.atr_window = self.params.get("atr_window", 14)
        self.atr_multiplier = self.params.get("atr_multiplier", 2.0)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["ema"] = ema(df["close"], self.ema_window)
        df["atr"] = atr(df[["high", "low", "close"]], self.atr_window)
        df["signal"] = 0

        for idx in range(1, len(df)):
            prev_close = df.iloc[idx - 1]["close"]
            curr_close = df.iloc[idx]["close"]
            prev_ema = df.iloc[idx - 1]["ema"]
            curr_ema = df.iloc[idx]["ema"]
            if np.isnan(prev_ema) or np.isnan(curr_ema):
                continue
            if prev_close <= prev_ema and curr_close > curr_ema:
                df.at[df.index[idx], "signal"] = 1
            elif prev_close >= prev_ema and curr_close < curr_ema:
                df.at[df.index[idx], "signal"] = -1

        return df[["signal"]]
