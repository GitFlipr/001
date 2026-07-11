import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import talib

class RSIDivergenceRelaxedStrategy(Strategy):
    """RSI DIVERGENCE RELAXED strategy - relaxed RSI divergence detection"""
    
    def init(self):
        close = self.data.Close
        self.rsi = self.I(talib.RSI, close, timeperiod=14)
    
    def next(self):
        if len(self.data) < 30:
            return
        
        # Check for NaN values
        if np.isnan(self.rsi[-1]):
            return
        
        current_rsi = self.rsi[-1]
        current_price = self.data.Close[-1]
        
        # Relaxed RSI conditions
        rsi_oversold = current_rsi < 35  # Relaxed from 30
        rsi_overbought = current_rsi > 65  # Relaxed from 70
        
        # Price relative to moving average
        price_above_ma = current_price > self.data.Close[-20:].mean()
        price_below_ma = current_price < self.data.Close[-20:].mean()
        
        # Volume confirmation
        volume_ok = self.data.Volume[-1] > self.data.Volume[-10:].mean() * 0.8
        
        # RELAXED RSI divergence conditions
        bullish_divergence = rsi_oversold and price_below_ma and volume_ok
        bearish_divergence = rsi_overbought and price_above_ma
        
        if bullish_divergence and not self.position:
            # Position sizing: Use 25% of equity per trade (fraction)
            position_size = 0.25
            
            # Risk management: 2% stop loss, 4% take profit
            entry_price = self.data.Close[-1]
            stop_loss = entry_price * 0.98  # 2% stop loss
            take_profit = entry_price * 1.04  # 4% take profit
            
            self.buy(size=position_size, sl=stop_loss, tp=take_profit)
        elif self.position and (rsi_overbought or price_above_ma):
            self.position.close()
