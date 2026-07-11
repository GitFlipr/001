import pandas as pd

from backtest.strategies.base import Strategy


class SeasonalityWindow(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.month = self.params.get("month", 1)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["month"] = df.index.month
        df["signal"] = 0
        df.loc[df["month"] == self.month, "signal"] = 1
        df.loc[df["month"] != self.month, "signal"] = -1
        return df[["signal"]]


class SeasonalRange(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["range"] = (df["high"] - df["low"]).rolling(self.window).mean()
        df["signal"] = 0
        df.loc[df["range"] > df["range"].shift(1), "signal"] = 1
        df.loc[df["range"] < df["range"].shift(1), "signal"] = -1
        return df[["signal"]]


class SeasonalTilt(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 30)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["trend"] = df["close"].rolling(self.window).mean().diff()
        df["signal"] = 0
        df.loc[df["trend"] > 0, "signal"] = 1
        df.loc[df["trend"] < 0, "signal"] = -1
        return df[["signal"]]
