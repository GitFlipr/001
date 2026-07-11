from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


class KeltnerBreakout(Strategy):
    # Define the strategy parameters
    ema_period = 20  # EMA period for the middle line
    atr_period = 10  # ATR period for channel width
    atr_multiplier = 2.0  # ATR multiplier for channel width
    rsi_period = 14  # RSI period for confirmation
    rsi_overbought = 70  # RSI overbought threshold
    rsi_oversold = 30  # RSI oversold threshold
    
    def init(self):
        # Calculate EMA for the middle line
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        
        # Calculate ATR for channel width
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # Calculate upper and lower Keltner Channels
        self.upper_channel = self.ema + (self.atr * self.atr_multiplier)
        self.lower_channel = self.ema - (self.atr * self.atr_multiplier)
        
        # Calculate RSI for confirmation
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        
        # Calculate volume SMA for confirmation
        self.volume_sma = self.I(_rolling_mean, self.data.Volume, 20)
    
    def next(self):
        # Check if we have a position
        if not self.position:
            # Long entry conditions:
            # 1. Price breaks above upper channel
            # 2. RSI is not overbought
            # 3. Volume is above average
            if (self.data.Close[-1] > self.upper_channel[-1] and
                self.rsi[-1] < self.rsi_overbought and
                self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss at lower channel
                stop_loss = self.lower_channel[-1]
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] + (self.atr[-1] * 2)
                self.buy(sl=stop_loss, tp=take_profit)
            
            # Short entry conditions:
            # 1. Price breaks below lower channel
            # 2. RSI is not oversold
            # 3. Volume is above average
            elif (self.data.Close[-1] < self.lower_channel[-1] and
                  self.rsi[-1] > self.rsi_oversold and
                  self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss at upper channel
                stop_loss = self.upper_channel[-1]
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] - (self.atr[-1] * 2)
                self.sell(sl=stop_loss, tp=take_profit)
        
        # Exit conditions
        else:
            # Long exit: Price crosses below EMA or RSI becomes overbought
            if self.position.is_long:
                if (self.data.Close[-1] < self.ema[-1] or
                    self.rsi[-1] >= self.rsi_overbought):
                    self.position.close()
            
            # Short exit: Price crosses above EMA or RSI becomes oversold
            elif self.position.is_short:
                if (self.data.Close[-1] > self.ema[-1] or
                    self.rsi[-1] <= self.rsi_oversold):
                    self.position.close()
