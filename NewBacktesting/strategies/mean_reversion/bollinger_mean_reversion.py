"""
Bollinger Bands Mean Reversion Strategy
Classic mean reversion using Bollinger Band extremes
"""
import pandas as pd
from backtest.strategies.base import Strategy
from backtest.utils.indicators import bollinger_bands, rsi


class BollingerMeanReversion(Strategy):
    """
    Bollinger Bands mean reversion strategy.
    
    Assumes price will revert to the mean (middle band).
    Entry when price touches/extends beyond bands with RSI confirmation.
    Exit when price reaches middle band or opposite band.
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.bb_period = self.params.get("bb_period", 20)
        self.bb_std = self.params.get("bb_std", 2.0)
        self.rsi_period = self.params.get("rsi_period", 14)
        self.rsi_oversold = self.params.get("rsi_oversold", 30)
        self.rsi_overbought = self.params.get("rsi_overbought", 70)
    
    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        
        df = self.data.copy()
        
        # Calculate Bollinger Bands
        upper, middle, lower = bollinger_bands(df["close"], self.bb_period, self.bb_std)
        df["bb_upper"] = upper
        df["bb_middle"] = middle
        df["bb_lower"] = lower
        
        # Calculate RSI for confirmation
        df["rsi"] = rsi(df["close"], self.rsi_period)
        
        # Initialize signals
        df["signal"] = 0
        
        # Long: Price at/below lower band AND RSI oversold
        long_condition = (df["low"] <= df["bb_lower"]) & (df["rsi"] < self.rsi_oversold)
        df.loc[long_condition, "signal"] = 1
        
        # Short: Price at/above upper band AND RSI overbought
        short_condition = (df["high"] >= df["bb_upper"]) & (df["rsi"] > self.rsi_overbought)
        df.loc[short_condition, "signal"] = -1
        
        return df[["signal"]]
