import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, rsi


class MiscBias(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.period = self.params.get("period", 10)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["ema"] = ema(df["close"], self.period)
        df["signal"] = 0
        df.loc[df["close"] > df["ema"], "signal"] = 1
        df.loc[df["close"] < df["ema"], "signal"] = -1
        return df[["signal"]]


class MiscCountertrend(Strategy):
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


class MiscSwing(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 5)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["ret"] = df["close"].pct_change(self.window)
        df["signal"] = 0
        df.loc[df["ret"] > 0, "signal"] = 1
        df.loc[df["ret"] < 0, "signal"] = -1
        return df[["signal"]]
