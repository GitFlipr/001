import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, rsi


class ExperimentalBlend(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.fast = self.params.get("fast", 5)
        self.slow = self.params.get("slow", 20)
        self.rsi_period = self.params.get("rsi_period", 14)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["ema_fast"] = ema(df["close"], self.fast)
        df["ema_slow"] = ema(df["close"], self.slow)
        df["rsi"] = rsi(df["close"], self.rsi_period)
        df["signal"] = 0
        df.loc[(df["ema_fast"] > df["ema_slow"]) & (df["rsi"] < 50), "signal"] = 1
        df.loc[(df["ema_fast"] < df["ema_slow"]) & (df["rsi"] > 50), "signal"] = -1
        return df[["signal"]]


class ExperimentalMeanReversion(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.period = self.params.get("period", 14)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["rsi"] = rsi(df["close"], self.period)
        df["signal"] = 0
        df.loc[df["rsi"] < 30, "signal"] = 1
        df.loc[df["rsi"] > 70, "signal"] = -1
        return df[["signal"]]


class ExperimentalMomentum(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.period = self.params.get("period", 10)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["roc"] = df["close"].pct_change(self.period) * 100
        df["signal"] = 0
        df.loc[df["roc"] > 5, "signal"] = 1
        df.loc[df["roc"] < -5, "signal"] = -1
        return df[["signal"]]
