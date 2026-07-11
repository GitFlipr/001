import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, rsi


class ScalpingPulse(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.fast = self.params.get("fast", 5)
        self.rsi_period = self.params.get("rsi_period", 7)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["ema_fast"] = ema(df["close"], self.fast)
        df["rsi"] = rsi(df["close"], self.rsi_period)
        df["signal"] = 0
        df.loc[(df["close"] > df["ema_fast"]) & (df["rsi"] < 40), "signal"] = 1
        df.loc[(df["close"] < df["ema_fast"]) & (df["rsi"] > 60), "signal"] = -1
        return df[["signal"]]


class ScalpingQuickRev(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 3)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["ret"] = df["close"].pct_change(self.window)
        df["signal"] = 0
        df.loc[df["ret"] > 0.01, "signal"] = 1
        df.loc[df["ret"] < -0.01, "signal"] = -1
        return df[["signal"]]


class ScalpingVolatility(Strategy):
    def __init__(self, params=None):
        super().__init__(params)
        self.window = self.params.get("window", 10)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["volatility"] = df["close"].pct_change().rolling(self.window).std()
        df["signal"] = 0
        df.loc[df["volatility"] > df["volatility"].rolling(5).mean(), "signal"] = 1
        df.loc[df["volatility"] < df["volatility"].rolling(5).mean(), "signal"] = -1
        return df[["signal"]]
