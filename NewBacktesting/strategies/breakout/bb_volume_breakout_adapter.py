"""
Bollinger Bands Volume Breakout Strategy
Adapted to use the base Strategy interface
"""
import pandas as pd
import numpy as np
from backtest.strategies.base import Strategy
from backtest.utils.indicators import bollinger_bands, sma


class BBVolumeBreakout(Strategy):
    """
    Bollinger Bands breakout with volume confirmation.
    
    Combines Bollinger Band breakouts with volume surge detection
    to filter false breakouts.
    
    Entry: Price breaks out of BB with volume > threshold * avg volume
    Exit: Price crosses back inside bands or reaches middle band
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.bb_period = self.params.get("bb_period", 20)
        self.bb_std = self.params.get("bb_std", 2.0)
        self.volume_ma_period = self.params.get("volume_ma_period", 20)
        self.volume_threshold = self.params.get("volume_threshold", 1.5)
    
    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        
        df = self.data.copy()
        
        # Calculate Bollinger Bands
        upper, middle, lower = bollinger_bands(df["close"], self.bb_period, self.bb_std)
        df["bb_upper"] = upper
        df["bb_middle"] = middle
        df["bb_lower"] = lower
        
        # Calculate Volume MA
        df["volume_ma"] = sma(df["volume"], self.volume_ma_period)
        
        # Initialize signals
        df["signal"] = 0
        
        # Volume surge confirmation
        volume_surge = df["volume"] > (self.volume_threshold * df["volume_ma"])
        
        # Upper breakout: Price closes above upper band with volume surge
        prev_below_upper = df["close"].shift(1) <= df["bb_upper"].shift(1)
        current_above_upper = df["close"] > df["bb_upper"]
        long_breakout = prev_below_upper & current_above_upper & volume_surge
        df.loc[long_breakout, "signal"] = 1
        
        # Lower breakout: Price closes below lower band with volume surge
        prev_above_lower = df["close"].shift(1) >= df["bb_lower"].shift(1)
        current_below_lower = df["close"] < df["bb_lower"]
        short_breakout = prev_above_lower & current_below_lower & volume_surge
        df.loc[short_breakout, "signal"] = -1
        
        return df[["signal"]]
