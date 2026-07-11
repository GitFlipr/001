from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib


def _vwap_from_data(data):
    typical = (data.High + data.Low + data.Close) / 3.0
    vol = np.asarray(data.Volume, dtype=float)
    return np.cumsum(vol * np.asarray(typical, dtype=float)) / np.maximum(np.cumsum(vol), 1e-12)


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


class VWAPBreakout(Strategy):
    # Define the strategy parameters
    vwap_period = 20  # VWAP period
    atr_period = 14  # ATR period for stop loss
    atr_multiplier = 2.0  # ATR multiplier for stop loss
    
    def init(self):
        # Calculate VWAP
        self.vwap = self.I(_vwap_from_data, self.data)
        
        # Calculate ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # Calculate volume SMA for confirmation
        self.volume_sma = self.I(_rolling_mean, self.data.Volume, 20)
        
        # Store recent highs and lows for breakout detection
        self.recent_highs = []
        self.recent_lows = []
    
    def next(self):
        # Update recent highs and lows
        if len(self.recent_highs) >= 2:
            self.recent_highs.pop(0)
        if len(self.recent_lows) >= 2:
            self.recent_lows.pop(0)
        
        self.recent_highs.append(self.data.High[-1])
        self.recent_lows.append(self.data.Low[-1])
        
        # Check if we have a position
        if not self.position:
            # Long entry conditions:
            # 1. Two consecutive closes above VWAP
            # 2. Price breaks above recent high
            # 3. Volume is above average
            if (len(self.recent_highs) >= 2 and
                self.data.Close[-1] > self.vwap[-1] and
                self.data.Close[-2] > self.vwap[-2] and
                self.data.Close[-1] > max(self.recent_highs[:-1]) and
                self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss at VWAP or recent low
                stop_loss = min(self.vwap[-1], min(self.recent_lows))
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] + (self.atr[-1] * 2)
                self.buy(sl=stop_loss, tp=take_profit)
            
            # Short entry conditions:
            # 1. Two consecutive closes below VWAP
            # 2. Price breaks below recent low
            # 3. Volume is above average
            elif (len(self.recent_lows) >= 2 and
                  self.data.Close[-1] < self.vwap[-1] and
                  self.data.Close[-2] < self.vwap[-2] and
                  self.data.Close[-1] < min(self.recent_lows[:-1]) and
                  self.data.Volume[-1] > self.volume_sma[-1]):
                # Set stop loss at VWAP or recent high
                stop_loss = max(self.vwap[-1], max(self.recent_highs))
                # Set take profit at 2x ATR
                take_profit = self.data.Close[-1] - (self.atr[-1] * 2)
                self.sell(sl=stop_loss, tp=take_profit)
        
        # Exit conditions
        else:
            # Long exit: Price crosses below VWAP or trailing stop
            if self.position.is_long:
                if self.data.Close[-1] < self.vwap[-1]:
                    self.position.close()
            
            # Short exit: Price crosses above VWAP or trailing stop
            elif self.position.is_short:
                if self.data.Close[-1] > self.vwap[-1]:
                    self.position.close()
