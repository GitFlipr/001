"""
VWMA Volume Flow Strategy
Volume-Weighted Moving Average with volume flow confirmation
"""
import pandas as pd
from backtest.strategies.base import Strategy
from backtest.utils.indicators import sma


class VWMAVolumeFlow(Strategy):
    """
    Volume-Weighted Moving Average with volume flow strategy.
    
    Combines VWMA for price direction with volume flow analysis
    to confirm institutional buying/selling pressure.
    
    Entry: Price crosses VWMA with strong volume flow
    Exit: Price crosses back or volume flow reverses
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.vwma_period = self.params.get("vwma_period", 20)
        self.volume_ma_period = self.params.get("volume_ma_period", 20)
        self.volume_bull_threshold = self.params.get("volume_bull_threshold", 1.3)
        self.volume_bear_threshold = self.params.get("volume_bear_threshold", 1.2)
    
    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        
        df = self.data.copy()
        
        # Calculate VWMA: sum(price * volume) / sum(volume)
        pv = df["close"] * df["volume"]
        df["vwma"] = pv.rolling(window=self.vwma_period).sum() / df["volume"].rolling(window=self.vwma_period).sum()
        
        # Volume MA
        df["volume_ma"] = sma(df["volume"], self.volume_ma_period)
        
        # Initialize signals
        df["signal"] = 0
        
        # Price position relative to VWMA
        above_vwma = df["close"] > df["vwma"]
        below_vwma = df["close"] < df["vwma"]
        
        # Volume flow: bullish when above average, bearish when below
        bull_volume = df["volume"] > (self.volume_bull_threshold * df["volume_ma"])
        bear_volume = df["volume"] > (self.volume_bear_threshold * df["volume_ma"])
        
        # Crossover detection
        prev_above = above_vwma.shift(1)
        prev_below = below_vwma.shift(1)
        
        # Long: Price crosses above VWMA with bull volume
        long_signal = (~prev_above & above_vwma) & bull_volume
        df.loc[long_signal, "signal"] = 1
        
        # Short: Price crosses below VWMA with bear volume
        short_signal = (~prev_below & below_vwma) & bear_volume
        df.loc[short_signal, "signal"] = -1
        
        return df[["signal"]]
