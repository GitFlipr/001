from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np
import talib

class MACross(Strategy):
    fast_period = 50
    slow_period = 200

    def init(self):
        self.fast_ma = self.I(talib.SMA, self.data.Close, timeperiod=self.fast_period)
        self.slow_ma = self.I(talib.SMA, self.data.Close, timeperiod=self.slow_period)
        
        # Calculate RSI for additional confirmation
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        
        # Calculate Bollinger Bands
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, self.data.Close)
    def next(self):
        if len(self.data) < 80:
            return
        # Check if we have a position
        if not self.position:
            # Golden Cross: Fast MA crosses above Slow MA
            # Additional conditions:
            # 1. RSI not overbought (< 70)
            # 2. Price not too far above upper Bollinger Band
            if (crossover(self.fast_ma, self.slow_ma) and
                self.rsi[-1] < 70 and
                self.data.Close[-1] < self.bb_upper[-1] * 1.05):
                self.buy()
            
            # Death Cross: Fast MA crosses below Slow MA
            # Additional conditions:
            # 1. RSI not oversold (> 30)
            # 2. Price not too far below lower Bollinger Band
            elif (crossover(self.slow_ma, self.fast_ma) and
                  self.rsi[-1] > 30 and
                  self.data.Close[-1] > self.bb_lower[-1] * 0.95):
                self.sell()
        
        # Exit conditions
        else:
            # Long exit: Death Cross or price below slow MA
            if self.position.is_long:
                if (crossover(self.slow_ma, self.fast_ma) or
                    self.data.Close[-1] < self.slow_ma[-1]):
                    self.position.close()
            
            # Short exit: Golden Cross or price above slow MA
            elif self.position.is_short:
                if (crossover(self.fast_ma, self.slow_ma) or
                    self.data.Close[-1] > self.slow_ma[-1]):
                    self.position.close()
