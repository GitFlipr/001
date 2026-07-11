"""
Bollinger Bands Breakout Strategy
"""
import pandas as pd
from backtest.strategies.base import Strategy
from backtest.utils.indicators import bollinger_bands


class BollingerBreakout(Strategy):
    """
    Long when price closes above upper band, short when below lower band
    """
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.bollinger_period = self.params.get("bollinger_period", 20)
        self.num_std = self.params.get("num_std", 2.0)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        upper, middle, lower = bollinger_bands(df["close"], self.bollinger_period, self.num_std)
        df["upper"] = upper
        df["middle"] = middle
        df["lower"] = lower
        df["signal"] = 0
        df.loc[df["close"] > df["upper"], "signal"] = 1
        df.loc[df["close"] < df["lower"], "signal"] = -1
        return df[["signal"]]
