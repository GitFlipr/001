import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, rsi, sma


class MeanReversionBounce(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.rsi_period = self.params.get("rsi_period", 14)
        self.ma_period = self.params.get("ma_period", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["rsi"] = rsi(df["close"], self.rsi_period)
        df["ma"] = sma(df["close"], self.ma_period)
        df["signal"] = 0
        df.loc[(df["rsi"] < 35) & (df["close"] < df["ma"]), "signal"] = 1
        df.loc[(df["rsi"] > 65) & (df["close"] > df["ma"]), "signal"] = -1
        return df[["signal"]]


class MeanReversionPullback(Strategy):
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
        df.loc[(df["ema_fast"] < df["ema_slow"]) & (df["close"] < df["ema_fast"]), "signal"] = 1
        df.loc[(df["ema_fast"] > df["ema_slow"]) & (df["close"] > df["ema_fast"]), "signal"] = -1
        return df[["signal"]]


class MeanReversionRange(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 15)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["high_roll"] = df["high"].rolling(self.window).max()
        df["low_roll"] = df["low"].rolling(self.window).min()
        df["signal"] = 0
        df.loc[df["close"] < df["low_roll"] + (df["high_roll"] - df["low_roll"]) * 0.25, "signal"] = 1
        df.loc[df["close"] > df["high_roll"] - (df["high_roll"] - df["low_roll"]) * 0.25, "signal"] = -1
        return df[["signal"]]
