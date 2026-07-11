from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib


def _range_high(data, window):
    return pd.Series(data.High).rolling(window).max().to_numpy()


def _range_low(data, window):
    return pd.Series(data.Low).rolling(window).min().to_numpy()


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


class RangeLiquidity(Strategy):
    # Define the strategy parameters
    range_period = 20  # Period to identify range
    atr_period = 14  # ATR period for stop loss
    atr_multiplier = 2.0  # ATR multiplier for stop loss
    
    def init(self):
        # Calculate range high and low
        self.range_high = self.I(_range_high, self.data, self.range_period)
        self.range_low = self.I(_range_low, self.data, self.range_period)
        
        # Calculate range middle
        self.range_middle = (self.range_high + self.range_low) / 2
        
        # Calculate ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # Calculate volume SMA for confirmation
        self.volume_sma = self.I(_rolling_mean, self.data.Volume, 20)
    
    def next(self):
        # Check if we have a position
        if not self.position:
            # Long entry conditions:
            # 1. Price breaks below range and then returns
            # 2. Volume is above average
            if (self.data.Low[-2] < self.range_low[-2] and
                self.data.Close[-1] > self.range_low[-1] and
                self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss below recent low
                stop_loss = min(self.data.Low[-5:])
                # Set take profit at range middle
                take_profit = self.range_middle[-1]
                self.buy(sl=stop_loss, tp=take_profit)
            
            # Short entry conditions:
            # 1. Price breaks above range and then returns
            # 2. Volume is above average
            elif (self.data.High[-2] > self.range_high[-2] and
                  self.data.Close[-1] < self.range_high[-1] and
                  self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss above recent high
                stop_loss = max(self.data.High[-5:])
                # Set take profit at range middle
                take_profit = self.range_middle[-1]
                self.sell(sl=stop_loss, tp=take_profit)
        
        # Exit conditions
        else:
            # Long exit: Price reaches range middle or trailing stop
            if self.position.is_long:
                if self.data.Close[-1] >= self.range_middle[-1]:
                    self.position.close()
                else:
                    # Update trailing stop
                    new_stop = max(self.position.sl or 0, self.data.Close[-1] - (self.atr[-1] * self.atr_multiplier))
                    self.position.sl = new_stop
            
            # Short exit: Price reaches range middle or trailing stop
            elif self.position.is_short:
                if self.data.Close[-1] <= self.range_middle[-1]:
                    self.position.close()
                else:
                    # Update trailing stop
                    new_stop = min(self.position.sl or float('inf'), self.data.Close[-1] + (self.atr[-1] * self.atr_multiplier))
                    self.position.sl = new_stop
