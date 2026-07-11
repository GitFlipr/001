from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np
import talib


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


class QuadMA(Strategy):
    # Define the strategy parameters
    ma1_period = 5  # Fastest MA period
    ma2_period = 10  # Second MA period
    ma3_period = 20  # Third MA period
    ma4_period = 50  # Slowest MA period
    atr_period = 14  # ATR period for stop loss
    atr_multiplier = 2.0  # ATR multiplier for stop loss
    
    def init(self):
        # Calculate all four moving averages
        self.ma1 = self.I(talib.SMA, self.data.Close, timeperiod=self.ma1_period)
        self.ma2 = self.I(talib.SMA, self.data.Close, timeperiod=self.ma2_period)
        self.ma3 = self.I(talib.SMA, self.data.Close, timeperiod=self.ma3_period)
        self.ma4 = self.I(talib.SMA, self.data.Close, timeperiod=self.ma4_period)
        
        # Calculate ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # Calculate volume SMA for confirmation
        self.volume_sma = self.I(_rolling_mean, self.data.Volume, 20)
    
    def next(self):
        # Check if we have a position
        if not self.position:
            # Long entry conditions:
            # 1. Fastest MA crosses above all other MAs
            # 2. Volume is above average
            if (crossover(self.ma1, self.ma2) and
                crossover(self.ma1, self.ma3) and
                crossover(self.ma1, self.ma4) and
                self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss using ATR
                stop_loss = self.data.Close[-1] - (self.atr[-1] * self.atr_multiplier)
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] + (self.atr[-1] * 2)
                self.buy(sl=stop_loss, tp=take_profit)
            
            # Short entry conditions:
            # 1. Fastest MA crosses below all other MAs
            # 2. Volume is above average
            elif (crossover(self.ma2, self.ma1) and
                  crossover(self.ma3, self.ma1) and
                  crossover(self.ma4, self.ma1) and
                  self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss using ATR
                stop_loss = self.data.Close[-1] + (self.atr[-1] * self.atr_multiplier)
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] - (self.atr[-1] * 2)
                self.sell(sl=stop_loss, tp=take_profit)
        
        # Exit conditions
        else:
            # Long exit: Fastest MA crosses below any other MA
            if self.position.is_long:
                if (crossover(self.ma2, self.ma1) or
                    crossover(self.ma3, self.ma1) or
                    crossover(self.ma4, self.ma1)):
                    self.position.close()
                else:
                    # Update trailing stop
                    new_stop = max(self.position.sl or 0, self.data.Close[-1] - (self.atr[-1] * self.atr_multiplier))
                    self.position.sl = new_stop
            
            # Short exit: Fastest MA crosses above any other MA
            elif self.position.is_short:
                if (crossover(self.ma1, self.ma2) or
                    crossover(self.ma1, self.ma3) or
                    crossover(self.ma1, self.ma4)):
                    self.position.close()
                else:
                    # Update trailing stop
                    new_stop = min(self.position.sl or float('inf'), self.data.Close[-1] + (self.atr[-1] * self.atr_multiplier))
                    self.position.sl = new_stop
