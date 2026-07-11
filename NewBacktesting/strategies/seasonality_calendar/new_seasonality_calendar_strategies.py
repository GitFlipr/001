import pandas as pd

from backtest.strategies.base import Strategy


class CalendarBias(Strategy):
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


class CalendarMomentum(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.month = self.params.get("month", 3)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["month"] = df.index.month
        df["signal"] = 0
        df.loc[df["month"] >= self.month, "signal"] = 1
        df.loc[df["month"] < self.month, "signal"] = -1
        return df[["signal"]]


class CalendarRange(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.month = self.params.get("month", 6)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["month"] = df.index.month
        df["signal"] = 0
        df.loc[df["month"] <= self.month, "signal"] = 1
        df.loc[df["month"] > self.month, "signal"] = -1
        return df[["signal"]]
