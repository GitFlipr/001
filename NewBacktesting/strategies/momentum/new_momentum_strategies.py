import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, roc, sma


class MomentumAcceleration(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.period = self.params.get("period", 10)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["roc"] = roc(df["close"], self.period)
        df["signal"] = 0
        df.loc[df["roc"] > 5, "signal"] = 1
        df.loc[df["roc"] < -5, "signal"] = -1
        return df[["signal"]]


class MomentumStrength(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.fast = self.params.get("fast", 5)
        self.slow = self.params.get("slow", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["ema_fast"] = ema(df["close"], self.fast)
        df["ema_slow"] = ema(df["close"], self.slow)
        df["signal"] = 0
        df.loc[df["ema_fast"] > df["ema_slow"], "signal"] = 1
        df.loc[df["ema_fast"] < df["ema_slow"], "signal"] = -1
        return df[["signal"]]


class MomentumWake(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 14)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["sma"] = sma(df["close"], self.window)
        df["signal"] = 0
        df.loc[df["close"] > df["sma"], "signal"] = 1
        df.loc[df["close"] < df["sma"], "signal"] = -1
        return df[["signal"]]
