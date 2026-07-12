"""
VWMA Trend Strategy
Volume-Weighted Moving Average trend following with volume confirmation
"""
import pandas as pd
import numpy as np
from backtest.strategies.base import Strategy
from backtest.utils.indicators import crossover


class VWMATrend(Strategy):
    """
    Volume-Weighted Moving Average trend strategy.
    
    VWMA gives more weight to periods with higher volume,
    making it more responsive to significant price moves.
    
    Entry: Price crosses above/below VWMA with volume confirmation
    Exit: Price crosses back or volume dries up
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.vwma_period = self.params.get("vwma_period", 20)
        self.volume_ma_period = self.params.get("volume_ma_period", 20)
        self.volume_threshold = self.params.get("volume_threshold", 1.2)
    
    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        
        df = self.data.copy()
        
        # Calculate VWMA: sum(price * volume) / sum(volume)
        pv = df["close"] * df["volume"]
        df["vwma"] = pv.rolling(window=self.vwma_period).sum() / df["volume"].rolling(window=self.vwma_period).sum()
        
        # Volume MA for confirmation
        df["volume_ma"] = df["volume"].rolling(window=self.volume_ma_period).mean()
        
        # Initialize signals
        df["signal"] = 0
        
        # Volume confirmation: current volume > threshold * average volume
        volume_confirmed = df["volume"] > (self.volume_threshold * df["volume_ma"])
        
        # Price above VWMA
        above_vwma = df["close"] > df["vwma"]
        below_vwma = df["close"] < df["vwma"]
        
        # Generate signals on crossover with volume confirmation
        prev_above = above_vwma.shift(1)
        prev_below = below_vwma.shift(1)
        
        # Long: Price crosses above VWMA with volume surge
        long_signal = (~prev_above & above_vwma) & volume_confirmed
        df.loc[long_signal, "signal"] = 1
        
        # Short: Price crosses below VWMA with volume surge
        short_signal = (~prev_below & below_vwma) & volume_confirmed
        df.loc[short_signal, "signal"] = -1
        
        return df[["signal"]]
