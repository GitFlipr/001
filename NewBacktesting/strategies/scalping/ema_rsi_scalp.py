"""
EMA-RSI Scalping Strategy
Fast scalping strategy using EMA crossovers with RSI filter
"""
import pandas as pd
from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, rsi, crossover


class EMARSIScalp(Strategy):
    """
    Fast EMA-RSI scalping strategy.
    
    Combines fast EMA crossovers for entry timing with RSI 
    to avoid overbought/oversold traps.
    
    Designed for quick in-and-out trades on short timeframes.
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.fast_ema = self.params.get("fast_ema", 5)
        self.slow_ema = self.params.get("slow_ema", 13)
        self.rsi_period = self.params.get("rsi_period", 7)
        self.rsi_overbought = self.params.get("rsi_overbought", 75)
        self.rsi_oversold = self.params.get("rsi_oversold", 25)
    
    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        
        df = self.data.copy()
        
        # Calculate fast EMAs
        df["ema_fast"] = ema(df["close"], self.fast_ema)
        df["ema_slow"] = ema(df["close"], self.slow_ema)
        
        # Calculate RSI for filter
        df["rsi"] = rsi(df["close"], self.rsi_period)
        
        # Initialize signals
        df["signal"] = 0
        
        # EMA crossover signals
        ema_cross = crossover(df["ema_fast"], df["ema_slow"])
        
        # Long: EMA fast crosses above slow AND RSI not overbought
        long_signal = (ema_cross > 0) & (df["rsi"] < self.rsi_overbought)
        df.loc[long_signal, "signal"] = 1
        
        # Short: EMA fast crosses below slow AND RSI not oversold
        short_signal = (ema_cross < 0) & (df["rsi"] > self.rsi_oversold)
        df.loc[short_signal, "signal"] = -1
        
        return df[["signal"]]
