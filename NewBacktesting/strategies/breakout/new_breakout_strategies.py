import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, sma, bollinger_bands


class BreakoutMomentumBand(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.fast = self.params.get("fast", 8)
        self.slow = self.params.get("slow", 21)

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


class BreakoutRetest(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 10)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["high_max"] = df["high"].rolling(self.window).max()
        df["low_min"] = df["low"].rolling(self.window).min()
        df["signal"] = 0
        df.loc[df["close"] > df["high_max"].shift(1), "signal"] = 1
        df.loc[df["close"] < df["low_min"].shift(1), "signal"] = -1
        return df[["signal"]]


class BreakoutVolumeSpike(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["volume_ma"] = df["volume"].rolling(self.window).mean()
        df["signal"] = 0
        df.loc[(df["volume"] > df["volume_ma"] * 1.5) & (df["close"] > df["close"].shift(1)), "signal"] = 1
        df.loc[(df["volume"] > df["volume_ma"] * 1.5) & (df["close"] < df["close"].shift(1)), "signal"] = -1
        return df[["signal"]]
