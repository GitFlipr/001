import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import rsi, sma


class RSIMeanReversion(Strategy):
    """RSI mean-reversion strategy adapted to the migrated base interface."""

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.rsi_period = self.params.get("rsi_period", 7)
        self.overbought = self.params.get("overbought", 70)
        self.oversold = self.params.get("oversold", 30)
        self.ma_period = self.params.get("ma_period", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["rsi"] = rsi(df["close"], self.rsi_period)
        df["ma"] = sma(df["close"], self.ma_period)
        df["signal"] = 0
        long_entry = (df["rsi"] < self.oversold) & (df["close"] > df["ma"])
        short_entry = (df["rsi"] > self.overbought) & (df["close"] < df["ma"])
        df.loc[long_entry, "signal"] = 1
        df.loc[short_entry, "signal"] = -1
        return df[["signal"]]


class RSIMeanReversionRegime(RSIMeanReversion):
    """Compatibility alias for regime-style RSI mean reversion."""

    pass
