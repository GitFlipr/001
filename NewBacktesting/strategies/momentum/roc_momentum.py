"""
Rate of Change Momentum Strategy
Pure momentum strategy using Rate of Change indicator
"""
import pandas as pd
from backtest.strategies.base import Strategy
from backtest.utils.indicators import roc, sma


class ROCMomentum(Strategy):
    """
    Rate of Change momentum strategy.
    
    Captures pure price momentum by measuring the percentage 
    change in price over a lookback period.
    
    Entry: ROC crosses above/below threshold with trend confirmation
    Exit: ROC crosses back toward zero or reverses sign
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.roc_period = self.params.get("roc_period", 12)
        self.momentum_threshold = self.params.get("momentum_threshold", 5.0)
        self.ma_period = self.params.get("ma_period", 50)
    
    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        
        df = self.data.copy()
        
        # Calculate Rate of Change
        df["roc"] = roc(df["close"], self.roc_period)
        
        # Trend filter with SMA
        df["sma"] = sma(df["close"], self.ma_period)
        
        # Initialize signals
        df["signal"] = 0
        
        # Long: ROC crosses above positive threshold AND price above SMA
        prev_below_threshold = df["roc"].shift(1) < self.momentum_threshold
        current_above_threshold = df["roc"] > self.momentum_threshold
        above_sma = df["close"] > df["sma"]
        
        long_signal = prev_below_threshold & current_above_threshold & above_sma
        df.loc[long_signal, "signal"] = 1
        
        # Short: ROC crosses below negative threshold AND price below SMA
        prev_above_threshold = df["roc"].shift(1) > -self.momentum_threshold
        current_below_threshold = df["roc"] < -self.momentum_threshold
        below_sma = df["close"] < df["sma"]
        
        short_signal = prev_above_threshold & current_below_threshold & below_sma
        df.loc[short_signal, "signal"] = -1
        
        return df[["signal"]]
