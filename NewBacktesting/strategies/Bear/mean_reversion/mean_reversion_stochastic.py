from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib

class MeanReversionStochastic(Strategy):
    # Define the strategy parameters
    ma_period = 200  # Moving average period for mean reversion
    stoch_k = 14  # Stochastic %K period
    stoch_d = 3  # Stochastic %D period
    stoch_smooth = 3  # Stochastic smoothing
    stoch_upper = 80  # Stochastic upper threshold
    stoch_lower = 20  # Stochastic lower threshold
    atr_period = 14  # ATR period for stop loss
    atr_multiplier = 2.0  # ATR multiplier for stop loss
    
    def init(self):
        # Calculate Super Smoother Moving Average
        self.ma = self.I(talib.SMA, self.data.Close, timeperiod=self.ma_period)

        fk, sk, sd = self.stoch_k, self.stoch_smooth, self.stoch_d

        def _slow_k(high, low, close):
            k, _d = talib.STOCH(
                high,
                low,
                close,
                fastk_period=fk,
                slowk_period=sk,
                slowk_matype=0,
                slowd_period=sd,
                slowd_matype=0,
            )
            return k

        self.stoch_k = self.I(_slow_k, self.data.High, self.data.Low, self.data.Close)

        # Calculate ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)

        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
    
    def next(self):
        # Check if we have a position
        if not self.position:
            # Long entry conditions:
            # 1. Price is below moving average
            # 2. Stochastic crosses above lower threshold
            # 3. Volume is above average
            if (self.data.Close[-1] < self.ma[-1] and
                self.stoch_k[-1] > self.stoch_lower and
                self.stoch_k[-2] <= self.stoch_lower and
                self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss using ATR
                stop_loss = self.data.Close[-1] - (self.atr[-1] * self.atr_multiplier)
                # Set take profit at moving average
                take_profit = self.ma[-1]
                self.buy(sl=stop_loss, tp=take_profit)
            
            # Short entry conditions:
            # 1. Price is above moving average
            # 2. Stochastic crosses below upper threshold
            # 3. Volume is above average
            elif (self.data.Close[-1] > self.ma[-1] and
                  self.stoch_k[-1] < self.stoch_upper and
                  self.stoch_k[-2] >= self.stoch_upper and
                  self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss using ATR
                stop_loss = self.data.Close[-1] + (self.atr[-1] * self.atr_multiplier)
                # Set take profit at moving average
                take_profit = self.ma[-1]
                self.sell(sl=stop_loss, tp=take_profit)
        
        # Exit conditions
        else:
            # Long exit: Price reaches moving average
            if self.position.is_long:
                if self.data.Close[-1] >= self.ma[-1]:
                    self.position.close()
            
            # Short exit: Price reaches moving average
            elif self.position.is_short:
                if self.data.Close[-1] <= self.ma[-1]:
                    self.position.close()
