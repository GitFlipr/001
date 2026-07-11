from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib

class PLDot(Strategy):
    # Define the strategy parameters
    pl_period = 20  # PL dot period
    atr_period = 14  # ATR period for stop loss
    atr_multiplier = 2.0  # ATR multiplier for stop loss
    
    def init(self):
        # Calculate PL dot (average of high, low, and close)
        self.pl_dot = self.I(lambda x: (x.High + x.Low + x.Close) / 3, self.data)
        
        # Calculate PL dot moving average
        self.pl_ma = self.I(lambda x: x.rolling(self.pl_period).mean(), self.pl_dot)
        
        # Calculate ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # Calculate volume SMA for confirmation
        self.volume_sma = self.I(lambda x: x.rolling(20).mean(), self.data.Volume)
    
    def next(self):
        # Check if we have a position
        if not self.position:
            # Long entry conditions:
            # 1. Price is above PL dot
            # 2. PL dot is above its moving average
            # 3. Volume is above average
            if (self.data.Close[-1] > self.pl_dot[-1] and
                self.pl_dot[-1] > self.pl_ma[-1] and
                self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss using ATR
                stop_loss = self.data.Close[-1] - (self.atr[-1] * self.atr_multiplier)
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] + (self.atr[-1] * 2)
                self.buy(sl=stop_loss, tp=take_profit)
            
            # Short entry conditions:
            # 1. Price is below PL dot
            # 2. PL dot is below its moving average
            # 3. Volume is above average
            elif (self.data.Close[-1] < self.pl_dot[-1] and
                  self.pl_dot[-1] < self.pl_ma[-1] and
                  self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss using ATR
                stop_loss = self.data.Close[-1] + (self.atr[-1] * self.atr_multiplier)
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] - (self.atr[-1] * 2)
                self.sell(sl=stop_loss, tp=take_profit)
        
        # Exit conditions
        else:
            # Long exit: Price crosses below PL dot or trailing stop
            if self.position.is_long:
                if self.data.Close[-1] < self.pl_dot[-1]:
                    self.position.close()
                else:
                    # Update trailing stop
                    new_stop = max(self.position.sl or 0, self.data.Close[-1] - (self.atr[-1] * self.atr_multiplier))
                    self.position.sl = new_stop
            
            # Short exit: Price crosses above PL dot or trailing stop
            elif self.position.is_short:
                if self.data.Close[-1] > self.pl_dot[-1]:
                    self.position.close()
                else:
                    # Update trailing stop
                    new_stop = min(self.position.sl or float('inf'), self.data.Close[-1] + (self.atr[-1] * self.atr_multiplier))
                    self.position.sl = new_stop
