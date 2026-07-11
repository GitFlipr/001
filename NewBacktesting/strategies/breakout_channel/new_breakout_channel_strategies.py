import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import sma


class ChannelBreakout(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["high_roll"] = df["high"].rolling(self.window).max()
        df["low_roll"] = df["low"].rolling(self.window).min()
        df["signal"] = 0
        df.loc[df["close"] > df["high_roll"].shift(1), "signal"] = 1
        df.loc[df["close"] < df["low_roll"].shift(1), "signal"] = -1
        return df[["signal"]]


class ChannelMomentum(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 10)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["sma"] = sma(df["close"], self.window)
        df["signal"] = 0
        df.loc[df["close"] > df["sma"], "signal"] = 1
        df.loc[df["close"] < df["sma"], "signal"] = -1
        return df[["signal"]]


class ChannelRetest(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 12)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["high_roll"] = df["high"].rolling(self.window).max()
        df["low_roll"] = df["low"].rolling(self.window).min()
        df["signal"] = 0
        df.loc[(df["close"] > df["high_roll"].shift(1)) & (df["close"].shift(1) < df["high_roll"].shift(1)), "signal"] = 1
        df.loc[(df["close"] < df["low_roll"].shift(1)) & (df["close"].shift(1) > df["low_roll"].shift(1)), "signal"] = -1
        return df[["signal"]]
