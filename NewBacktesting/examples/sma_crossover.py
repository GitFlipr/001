"""
Example: Simple Moving Average Crossover Strategy
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import pandas as pd
import numpy as np
from backtest.strategies.base import Strategy


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
        df = self.data.copy()
        
        # Calculate moving averages
        df["sma_short"] = df["close"].rolling(window=self.short_window).mean()
        df["sma_long"] = df["close"].rolling(window=self.long_window).mean()
        
        # Generate signals
        df["signal"] = 0
        # Long when short SMA crosses above long SMA
        df.loc[df["sma_short"] > df["sma_long"], "signal"] = 1
        # Short when short SMA crosses below long SMA
        df.loc[df["sma_short"] < df["sma_long"], "signal"] = -1
        
        return df[["signal"]]


if __name__ == "__main__":
    print("SMACrossover strategy example loaded!")
