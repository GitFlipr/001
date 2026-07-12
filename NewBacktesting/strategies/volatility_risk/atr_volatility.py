"""
ATR Volatility Strategy
Volatility-based position sizing and entry timing using ATR
"""
import pandas as pd
from backtest.strategies.base import Strategy
from backtest.utils.indicators import atr, sma


class ATRVolatility(Strategy):
    """
    ATR-based volatility strategy.
    
    Uses Average True Range to identify volatility regimes and 
    time entries during volatility expansion/contraction cycles.
    
    Entry: When volatility expands after contraction (breakout potential)
    Exit: When volatility contracts or trend exhausts
    """
    
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.atr_period = self.params.get("atr_period", 14)
        self.atr_ma_period = self.params.get("atr_ma_period", 20)
        self.volatility_threshold = self.params.get("volatility_threshold", 1.5)
        self.ma_period = self.params.get("ma_period", 50)
    
    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        
        df = self.data.copy()
        
        # Calculate ATR and its moving average
        df["atr"] = atr(df, self.atr_period)
        df["atr_ma"] = sma(df["atr"], self.atr_ma_period)
        
        # Trend filter
        df["sma"] = sma(df["close"], self.ma_period)
        
        # Initialize signals
        df["signal"] = 0
        
        # Volatility expansion: ATR > threshold * ATR_MA
        vol_expansion = df["atr"] > (self.volatility_threshold * df["atr_ma"])
        
        # Long: Volatility expansion AND price above SMA (bullish trend)
        long_signal = vol_expansion & (df["close"] > df["sma"])
        df.loc[long_signal, "signal"] = 1
        
        # Short: Volatility expansion AND price below SMA (bearish trend)
        short_signal = vol_expansion & (df["close"] < df["sma"])
        df.loc[short_signal, "signal"] = -1
        
        return df[["signal"]]
