"""
Bull/Bear EMA + RSI scalping strategy migrated from the legacy backup set.
"""
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, rsi


class BullBearEMARsiScalping(Strategy):
    """
    Go long when the short EMA is above the long EMA and RSI is oversold.
    Go short when the short EMA is below the long EMA and RSI is overbought.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.short_ema_period = self.params.get("short_ema_period", 5)
        self.long_ema_period = self.params.get("long_ema_period", 20)
        self.rsi_period = self.params.get("rsi_period", 14)
        self.rsi_buy_level = self.params.get("rsi_buy_level", 40)
        self.rsi_sell_level = self.params.get("rsi_sell_level", 60)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["ema_short"] = ema(df["close"], self.short_ema_period)
        df["ema_long"] = ema(df["close"], self.long_ema_period)
        df["rsi"] = rsi(df["close"], self.rsi_period)

        df["signal"] = 0
        long_entry = (df["ema_short"] > df["ema_long"]) & (df["rsi"] < self.rsi_buy_level)
        short_entry = (df["ema_short"] < df["ema_long"]) & (df["rsi"] > self.rsi_sell_level)

        df.loc[long_entry, "signal"] = 1
        df.loc[short_entry, "signal"] = -1
        return df[["signal"]]
