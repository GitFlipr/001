"""
Triple EMA Trend Strategy
Uses three EMAs for trend confirmation and entry signals
"""
import pandas as pd
from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, crossover


class TripleEMATrend(Strategy):
    """
    Triple EMA crossover strategy for robust trend following.
    
    Uses three EMAs (fast, medium, slow) to confirm trend direction.
    Long signal: Fast > Medium > Slow (all aligned bullish)
    Short signal: Fast < Medium < Slow (all aligned bearish)
    Exit when alignment breaks
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.fast_period = self.params.get("fast_period", 9)
        self.medium_period = self.params.get("medium_period", 21)
        self.slow_period = self.params.get("slow_period", 50)
    
    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        
        df = self.data.copy()
        
        # Calculate three EMAs
        df["ema_fast"] = ema(df["close"], self.fast_period)
        df["ema_medium"] = ema(df["close"], self.medium_period)
        df["ema_slow"] = ema(df["close"], self.slow_period)
        
        # Initialize signals
        df["signal"] = 0
        
        # Bullish alignment: Fast > Medium > Slow
        bullish = (df["ema_fast"] > df["ema_medium"]) & (df["ema_medium"] > df["ema_slow"])
        # Bearish alignment: Fast < Medium < Slow
        bearish = (df["ema_fast"] < df["ema_medium"]) & (df["ema_medium"] < df["ema_slow"])
        
        # Generate signals on alignment change
        prev_bullish = bullish.shift(1)
        prev_bearish = bearish.shift(1)
        
        # Enter long when bullish alignment starts
        df.loc[bullish & ~prev_bullish, "signal"] = 1
        # Enter short when bearish alignment starts
        df.loc[bearish & ~prev_bearish, "signal"] = -1
        
        return df[["signal"]]
