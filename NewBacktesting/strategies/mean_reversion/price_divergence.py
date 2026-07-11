from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib

class PriceDivergence(Strategy):
    # Define the strategy parameters
    rsi_period = 14  # RSI period
    macd_fast = 12  # MACD fast period
    macd_slow = 26  # MACD slow period
    macd_signal = 9  # MACD signal period
    stoch_k = 14  # Stochastic %K period
    stoch_d = 3  # Stochastic %D period
    stoch_smooth = 3  # Stochastic smoothing
    atr_period = 14  # ATR period for stop loss
    atr_multiplier = 2.0  # ATR multiplier for stop loss
    
    def init(self):
        # Calculate RSI
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        
        # Calculate MACD
        self.macd, self.macd_signal, self.macd_hist = self.I(talib.MACD, self.data.Close,
                                                            fastperiod=self.macd_fast,
                                                            slowperiod=self.macd_slow,
                                                            signalperiod=self.macd_signal)
        
        # Calculate Stochastic
        self.stoch_k, self.stoch_d = self.I(talib.STOCH, self.data.High, self.data.Low, self.data.Close,
                                          fastk_period=self.stoch_k,
                                          slowk_period=self.stoch_smooth,
                                          slowk_matype=0,
                                          slowd_period=self.stoch_d,
                                          slowd_matype=0)
        
        # Calculate ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # Calculate volume SMA for confirmation
        self.volume_sma = self.I(lambda x: x.rolling(20).mean(), self.data.Volume)
        
        # Store recent price highs and lows for divergence detection
        self.price_highs = []
        self.price_lows = []
        self.rsi_highs = []
        self.rsi_lows = []
        self.macd_highs = []
        self.macd_lows = []
        self.stoch_highs = []
        self.stoch_lows = []
    
    def next(self):
        # Update recent highs and lows
        if len(self.price_highs) >= 2:
            self.price_highs.pop(0)
            self.price_lows.pop(0)
            self.rsi_highs.pop(0)
            self.rsi_lows.pop(0)
            self.macd_highs.pop(0)
            self.macd_lows.pop(0)
            self.stoch_highs.pop(0)
            self.stoch_lows.pop(0)
        
        self.price_highs.append(self.data.High[-1])
        self.price_lows.append(self.data.Low[-1])
        self.rsi_highs.append(self.rsi[-1])
        self.rsi_lows.append(self.rsi[-1])
        self.macd_highs.append(self.macd[-1])
        self.macd_lows.append(self.macd[-1])
        self.stoch_highs.append(self.stoch_k[-1])
        self.stoch_lows.append(self.stoch_k[-1])
        
        # Check if we have a position
        if not self.position:
            # Long entry conditions:
            # 1. Bullish divergence in at least two indicators
            # 2. Price action confirmation (higher low)
            # 3. Volume is above average
            bullish_divergence = (
                (len(self.price_lows) >= 2 and
                 self.price_lows[-1] < self.price_lows[-2] and
                 self.rsi_lows[-1] > self.rsi_lows[-2]) or
                (len(self.price_lows) >= 2 and
                 self.price_lows[-1] < self.price_lows[-2] and
                 self.macd_lows[-1] > self.macd_lows[-2]) or
                (len(self.price_lows) >= 2 and
                 self.price_lows[-1] < self.price_lows[-2] and
                 self.stoch_lows[-1] > self.stoch_lows[-2])
            )
            
            if (bullish_divergence and
                self.data.Close[-1] > self.data.Close[-2] and
                self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss using ATR
                stop_loss = self.data.Close[-1] - (self.atr[-1] * self.atr_multiplier)
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] + (self.atr[-1] * 2)
                self.buy(sl=stop_loss, tp=take_profit)
            
            # Short entry conditions:
            # 1. Bearish divergence in at least two indicators
            # 2. Price action confirmation (lower high)
            # 3. Volume is above average
            bearish_divergence = (
                (len(self.price_highs) >= 2 and
                 self.price_highs[-1] > self.price_highs[-2] and
                 self.rsi_highs[-1] < self.rsi_highs[-2]) or
                (len(self.price_highs) >= 2 and
                 self.price_highs[-1] > self.price_highs[-2] and
                 self.macd_highs[-1] < self.macd_highs[-2]) or
                (len(self.price_highs) >= 2 and
                 self.price_highs[-1] > self.price_highs[-2] and
                 self.stoch_highs[-1] < self.stoch_highs[-2])
            )
            
            if (bearish_divergence and
                self.data.Close[-1] < self.data.Close[-2] and
                self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss using ATR
                stop_loss = self.data.Close[-1] + (self.atr[-1] * self.atr_multiplier)
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] - (self.atr[-1] * 2)
                self.sell(sl=stop_loss, tp=take_profit)
        
        # Exit conditions
        else:
            # Long exit: Price makes lower low or trailing stop
            if self.position.is_long:
                if self.data.Close[-1] < self.data.Close[-2]:
                    self.position.close()
                else:
                    # Update trailing stop
                    new_stop = max(self.position.sl or 0, self.data.Close[-1] - (self.atr[-1] * self.atr_multiplier))
                    self.position.sl = new_stop
            
            # Short exit: Price makes higher high or trailing stop
            elif self.position.is_short:
                if self.data.Close[-1] > self.data.Close[-2]:
                    self.position.close()
                else:
                    # Update trailing stop
                    new_stop = min(self.position.sl or float('inf'), self.data.Close[-1] + (self.atr[-1] * self.atr_multiplier))
                    self.position.sl = new_stop
