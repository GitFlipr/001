"""
Stochastic Mean Reversion Strategy
Mean reversion using Stochastic oscillator extremes
"""
import pandas as pd
from backtest.strategies.base import Strategy
from backtest.utils.indicators import stoch_rsi, sma


class StochMeanReversion(Strategy):
    """
    Stochastic RSI mean reversion strategy.
    
    Uses Stochastic RSI to identify extreme oversold/overbought conditions
    for mean reversion entries. More sensitive than regular RSI.
    
    Entry: Stoch RSI crosses back from extreme levels
    Exit: Stoch RSI reaches middle zone or opposite extreme
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.rsi_period = self.params.get("rsi_period", 14)
        self.stoch_period = self.params.get("stoch_period", 14)
        self.smooth_k = self.params.get("smooth_k", 3)
        self.smooth_d = self.params.get("smooth_d", 3)
        self.oversold = self.params.get("oversold", 20)
        self.overbought = self.params.get("overbought", 80)
        self.ma_period = self.params.get("ma_period", 50)
    
    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        
        df = self.data.copy()
        
        # Calculate Stochastic RSI
        k, d = stoch_rsi(df["close"], self.rsi_period, self.stoch_period, 
                         self.smooth_k, self.smooth_d)
        df["stoch_k"] = k
        df["stoch_d"] = d
        
        # Trend filter with SMA
        df["sma"] = sma(df["close"], self.ma_period)
        
        # Initialize signals
        df["signal"] = 0
        
        # Long: Stoch K crosses above oversold level from below
        prev_oversold = df["stoch_k"].shift(1) < self.oversold
        current_above_oversold = df["stoch_k"] > self.oversold
        # Additional filter: price above SMA for bullish bias
        above_sma = df["close"] > df["sma"]
        
        long_signal = prev_oversold & current_above_oversold & above_sma
        df.loc[long_signal, "signal"] = 1
        
        # Short: Stoch K crosses below overbought level from above
        prev_overbought = df["stoch_k"].shift(1) > self.overbought
        current_below_overbought = df["stoch_k"] < self.overbought
        # Additional filter: price below SMA for bearish bias
        below_sma = df["close"] < df["sma"]
        
        short_signal = prev_overbought & current_below_overbought & below_sma
        df.loc[short_signal, "signal"] = -1
        
        return df[["signal"]]
