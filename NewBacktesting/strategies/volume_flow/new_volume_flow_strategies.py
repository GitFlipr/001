import pandas as pd

from backtest.strategies.base import Strategy


class FlowBias(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 10)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["volume_change"] = df["volume"].diff(self.window)
        df["signal"] = 0
        df.loc[df["volume_change"] > 0, "signal"] = 1
        df.loc[df["volume_change"] < 0, "signal"] = -1
        return df[["signal"]]


class FlowMomentum(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 5)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["change"] = df["close"].diff(self.window)
        df["signal"] = 0
        df.loc[(df["change"] > 0) & (df["volume"] > df["volume"].shift(1)), "signal"] = 1
        df.loc[(df["change"] < 0) & (df["volume"] > df["volume"].shift(1)), "signal"] = -1
        return df[["signal"]]


class FlowRange(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 15)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["volume_range"] = df["volume"].rolling(self.window).std()
        df["signal"] = 0
        df.loc[df["volume_range"] > df["volume_range"].shift(1), "signal"] = 1
        df.loc[df["volume_range"] < df["volume_range"].shift(1), "signal"] = -1
        return df[["signal"]]
