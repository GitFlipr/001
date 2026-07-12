"""
Keltner Channel Trend Strategy
Trend following using Keltner Channels (ATR-based bands)
"""
import pandas as pd
import numpy as np
from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, atr


class KeltnerTrend(Strategy):
    """
    Keltner Channel trend following strategy.
    
    Keltner Channels use ATR for volatility-based bands around an EMA.
    More adaptive than Bollinger Bands in trending markets.
    
    Entry: Price breaks out of channel in trend direction
    Exit: Price crosses middle EMA or opposite channel
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.ema_period = self.params.get("ema_period", 20)
        self.atr_period = self.params.get("atr_period", 10)
        self.atr_multiplier = self.params.get("atr_multiplier", 2.0)
    
    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        
        df = self.data.copy()
        
        # Calculate Keltner Channels
        df["middle"] = ema(df["close"], self.ema_period)
        df["atr"] = atr(df, self.atr_period)
        df["upper"] = df["middle"] + (self.atr_multiplier * df["atr"])
        df["lower"] = df["middle"] - (self.atr_multiplier * df["atr"])
        
        # Initialize signals
        df["signal"] = 0
        
        # Trend filter: price above/below middle EMA
        uptrend = df["close"] > df["middle"]
        downtrend = df["close"] < df["middle"]
        
        # Breakout signals
        prev_upper = df["upper"].shift(1)
        prev_lower = df["lower"].shift(1)
        
        # Long: Price breaks above upper channel in uptrend
        long_breakout = (df["close"] > df["upper"]) & (df["close"].shift(1) <= prev_upper) & uptrend
        df.loc[long_breakout, "signal"] = 1
        
        # Short: Price breaks below lower channel in downtrend
        short_breakout = (df["close"] < df["lower"]) & (df["close"].shift(1) >= prev_lower) & downtrend
        df.loc[short_breakout, "signal"] = -1
        
        return df[["signal"]]
