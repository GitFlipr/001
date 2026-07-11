"""
Bollinger + ROC scalping strategy adapted from the legacy script harness.
"""
import pandas as pd
import numpy as np

from backtest.strategies.base import Strategy
from backtest.utils.indicators import bollinger_bands, roc


class BollingerROCScalper(Strategy):
    """
    Long when price touches the lower Bollinger band and ROC turns positive.
    Short when price touches the upper Bollinger band and ROC turns negative.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.bb_period = self.params.get("bb_period", 20)
        self.bb_std = self.params.get("bb_std", 2.0)
        self.roc_period = self.params.get("roc_period", 14)
        self.touch_sensitivity = self.params.get("touch_sensitivity", 0.01)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        upper, middle, lower = bollinger_bands(df["close"], self.bb_period, self.bb_std)
        df["upper_band"] = upper
        df["middle_band"] = middle
        df["lower_band"] = lower
        df["roc"] = roc(df["close"], self.roc_period)
        df["signal"] = 0

        for idx in range(1, len(df)):
            close = df.iloc[idx]["close"]
            low_band = df.iloc[idx]["lower_band"]
            high_band = df.iloc[idx]["upper_band"]
            prev_roc = df.iloc[idx - 1]["roc"]
            cur_roc = df.iloc[idx]["roc"]
            if close <= low_band * (1 + self.touch_sensitivity) and prev_roc <= 0 and cur_roc > 0:
                df.at[df.index[idx], "signal"] = 1
            elif close >= high_band * (1 - self.touch_sensitivity) and prev_roc >= 0 and cur_roc < 0:
                df.at[df.index[idx], "signal"] = -1

        return df[["signal"]]
