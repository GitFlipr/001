"""
Simple Moving Average Crossover Strategy
"""
import pandas as pd
from backtest.strategies.base import Strategy
from backtest.utils.indicators import sma


class SMACrossover(Strategy):
    """
    Simple Moving Average Crossover Strategy
    """
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.short_window = self.params.get("short_window", 10)
        self.long_window = self.params.get("long_window", 50)

    def generate_signals(self) -> pd.DataFrame:
        """
        Generate signals based on moving average crossover
        
        Returns:
            DataFrame with 'signal' column
        """
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        
        # Calculate moving averages
        df["sma_short"] = sma(df["close"], self.short_window)
        df["sma_long"] = sma(df["close"], self.long_window)
        
        # Generate signals
        df["signal"] = 0
        # Long when short SMA crosses above long SMA
        df.loc[df["sma_short"] > df["sma_long"], "signal"] = 1
        # Short when short SMA crosses below long SMA
        df.loc[df["sma_short"] < df["sma_long"], "signal"] = -1
        
        return df[["signal"]]
