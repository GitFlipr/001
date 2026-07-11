import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import sma


class VolumeFlowBreak(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["volume_ma"] = df["volume"].rolling(self.window).mean()
        df["signal"] = 0
        df.loc[df["volume"] > df["volume_ma"] * 1.3, "signal"] = 1
        df.loc[df["volume"] < df["volume_ma"] * 0.7, "signal"] = -1
        return df[["signal"]]


class VolumePressure(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 15)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["price_ma"] = sma(df["close"], self.window)
        df["signal"] = 0
        df.loc[df["close"] > df["price_ma"], "signal"] = 1
        df.loc[df["close"] < df["price_ma"], "signal"] = -1
        return df[["signal"]]


class VolumeSurge(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 10)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["volume_sma"] = df["volume"].rolling(self.window).mean()
        df["signal"] = 0
        df.loc[(df["volume"] > df["volume_sma"] * 1.5) & (df["close"].diff() > 0), "signal"] = 1
        df.loc[(df["volume"] > df["volume_sma"] * 1.5) & (df["close"].diff() < 0), "signal"] = -1
        return df[["signal"]]
