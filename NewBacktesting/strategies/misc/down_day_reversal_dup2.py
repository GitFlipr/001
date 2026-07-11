from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib

class DownDayReversal(Strategy):
    # Define the strategy parameters
    consecutive_days = 4  # Number of consecutive down days to look for
    rsi_period = 14  # RSI period for confirmation
    
    def init(self):
        # Calculate RSI for confirmation
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        
        # Calculate ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=14)
    def next(self):
        if len(self.data) < 80:
            return
        # Check for consecutive down days
        down_days = 0
        for i in range(1, self.consecutive_days + 1):
            if self.data.Close[-i] < self.data.Close[-(i + 1)]:
                down_days += 1
            else:
                break
        
        # Check if we have a position
        if not self.position:
            # Buy conditions:
            # 1. Exactly 4 consecutive down days
            # 2. RSI is oversold (< 30)
            if down_days == self.consecutive_days and self.rsi[-1] < 30:
                # Calculate stop loss using ATR
                stop_loss = self.data.Close[-1] - self.atr[-1] * 2
                self.buy(sl=stop_loss)
        
        # Exit conditions
        else:
            # Exit after one day (as per strategy)
            if self.position.is_long:
                self.position.close()
