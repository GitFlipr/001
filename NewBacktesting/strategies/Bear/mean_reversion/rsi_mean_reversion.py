from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib

class RSIMeanReversion(Strategy):
    # Define the strategy parameters
    rsi_period = 7  # Short period RSI for faster signals
    overbought = 70  # Overbought threshold
    oversold = 30  # Oversold threshold
    atr_period = 14  # ATR period for stop loss
    atr_multiplier = 2.0  # ATR multiplier for stop loss
    
    def init(self):
        # Calculate RSI
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        
        # Calculate ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # Calculate volume SMA for confirmation
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
    
    def next(self):
        # Check if we have a position
        if not self.position:
            # Long entry conditions:
            # 1. RSI crosses above oversold level
            # 2. Volume above average
            if (self.rsi[-1] > self.oversold and
                self.rsi[-2] <= self.oversold and
                self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss using ATR
                stop_loss = self.data.Close[-1] - (self.atr[-1] * self.atr_multiplier)
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] + (self.atr[-1] * 2)
                self.buy(sl=stop_loss, tp=take_profit)
            
            # Short entry conditions:
            # 1. RSI crosses below overbought level
            # 2. Volume above average
            elif (self.rsi[-1] < self.overbought and
                  self.rsi[-2] >= self.overbought and
                  self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss using ATR
                stop_loss = self.data.Close[-1] + (self.atr[-1] * self.atr_multiplier)
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] - (self.atr[-1] * 2)
                self.sell(sl=stop_loss, tp=take_profit)
        
        # Exit conditions
        else:
            # Long exit: RSI reaches overbought
            if self.position.is_long:
                if self.rsi[-1] >= self.overbought:
                    self.position.close()
            
            # Short exit: RSI reaches oversold
            elif self.position.is_short:
                if self.rsi[-1] <= self.oversold:
                    self.position.close()
