import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import sma


class StatArbMeanReversion(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["spread"] = df["close"] - sma(df["close"], self.window)
        df["signal"] = 0
        df.loc[df["spread"] > 0, "signal"] = 1
        df.loc[df["spread"] < 0, "signal"] = -1
        return df[["signal"]]


class StatArbMomentum(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 10)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["momentum"] = df["close"].pct_change(self.window)
        df["signal"] = 0
        df.loc[df["momentum"] > 0, "signal"] = 1
        df.loc[df["momentum"] < 0, "signal"] = -1
        return df[["signal"]]


class StatArbSpread(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 15)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["spread"] = df["close"] - df["close"].rolling(self.window).mean()
        df["signal"] = 0
        df.loc[df["spread"] > df["spread"].shift(1), "signal"] = 1
        df.loc[df["spread"] < df["spread"].shift(1), "signal"] = -1
        return df[["signal"]]
