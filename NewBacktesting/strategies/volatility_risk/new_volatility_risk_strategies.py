import pandas as pd

from backtest.strategies.base import Strategy


class VolatilityCandle(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 10)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["range"] = (df["high"] - df["low"]).rolling(self.window).mean()
        df["signal"] = 0
        df.loc[df["range"] > df["range"].shift(1), "signal"] = 1
        df.loc[df["range"] < df["range"].shift(1), "signal"] = -1
        return df[["signal"]]


class VolatilityCompression(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["std"] = df["close"].pct_change().rolling(self.window).std()
        df["signal"] = 0
        df.loc[df["std"] < df["std"].rolling(5).mean(), "signal"] = 1
        df.loc[df["std"] > df["std"].rolling(5).mean(), "signal"] = -1
        return df[["signal"]]


class VolatilityRange(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 15)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["band"] = (df["high"] - df["low"]).rolling(self.window).mean()
        df["signal"] = 0
        df.loc[df["close"] > df["close"].shift(1) + df["band"], "signal"] = 1
        df.loc[df["close"] < df["close"].shift(1) - df["band"], "signal"] = -1
        return df[["signal"]]
