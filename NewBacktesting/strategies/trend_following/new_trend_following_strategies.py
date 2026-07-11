import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, sma


class TrendPulse(Strategy):
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


class TrendRibbon(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.periods = self.params.get("periods", [8, 13, 21])

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        for period in self.periods:
            df[f"ma_{period}"] = sma(df["close"], period)
        df["signal"] = 0
        if len(self.periods) >= 2:
            df.loc[df[f"ma_{self.periods[0]}"] > df[f"ma_{self.periods[-1]}"] , "signal"] = 1
            df.loc[df[f"ma_{self.periods[0]}"] < df[f"ma_{self.periods[-1]}"] , "signal"] = -1
        return df[["signal"]]


class TrendSlope(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["sma"] = sma(df["close"], self.window)
        df["slope"] = df["sma"].diff()
        df["signal"] = 0
        df.loc[df["slope"] > 0, "signal"] = 1
        df.loc[df["slope"] < 0, "signal"] = -1
        return df[["signal"]]
