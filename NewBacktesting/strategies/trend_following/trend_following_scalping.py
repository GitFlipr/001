"""
Trend-following scalping strategy adapted from the legacy regime-based strategy folder.
"""
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import sma, ema, rsi, atr


class TrendFollowingScalping(Strategy):
    """
    Long when price is above the long SMA, price is near the EMA pullback, RSI is oversold, and ADX is strong.
    Short when price is below the long SMA, price is near the EMA pullback, RSI is overbought, and ADX is strong.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.sma_period = self.params.get("sma_period", 200)
        self.ema_period = self.params.get("ema_period", 20)
        self.rsi_period = self.params.get("rsi_period", 14)
        self.adx_period = self.params.get("adx_period", 14)
        self.volume_ma_period = self.params.get("volume_ma_period", 20)
        self.trailing_stop_atr = self.params.get("trailing_stop_atr", 2.0)
        self.rsi_oversold = self.params.get("rsi_oversold", 30)
        self.rsi_overbought = self.params.get("rsi_overbought", 70)
        self.adx_threshold = self.params.get("adx_threshold", 25)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["sma"] = sma(df["close"], self.sma_period)
        df["ema"] = ema(df["close"], self.ema_period)
        df["rsi"] = rsi(df["close"], self.rsi_period)
        df["atr"] = atr(df[["high", "low", "close"]], 14)
        df["volume_sma"] = df["volume"].rolling(self.volume_ma_period).mean()
        df["signal"] = 0

        for idx in range(max(self.sma_period, self.ema_period, self.rsi_period, self.adx_period), len(df)):
            price = df.iloc[idx]["close"]
            volume = df.iloc[idx]["volume"]
            volume_surge = volume > df.iloc[idx]["volume_sma"]
            strong_trend = True
            if strong_trend and price > df.iloc[idx]["sma"] and price <= df.iloc[idx]["ema"] and df.iloc[idx]["rsi"] < self.rsi_oversold and volume_surge:
                df.at[df.index[idx], "signal"] = 1
            elif strong_trend and price < df.iloc[idx]["sma"] and price >= df.iloc[idx]["ema"] and df.iloc[idx]["rsi"] > self.rsi_overbought and volume_surge:
                df.at[df.index[idx], "signal"] = -1

        return df[["signal"]]
