"""
Ultra Bull Explosion Strategy - Q1 2025 Optimized
Priority 1 strategy from AllRegime Master Bot

Strategy Logic:
- Ultra-aggressive momentum detection
- Volume explosion confirmation
- Price above moving average
- Multiple momentum thresholds
- Fast entry/exit for explosive moves
"""

import numpy as np
from backtesting import Strategy
import talib


class UltraBullExplosionQ1(Strategy):
    """
    Q1 2025 Optimized Ultra Bull Explosion Strategy
    
    Entry Rules:
    - Any momentum (0.05% in 1 period OR 0.7% in 5 periods)
    - Volume surge (1.5x average) OR price above MA
    - Ultra-aggressive entry
    
    Exit Rules:
    - Price drops below MA * 0.95 (5% drop from MA)
    - ATR-based stop loss (1%)
    - ATR-based take profit (1.67%)
    """
    
    # Indicator parameters
    ma_period = 10
    volume_lookback = 10
    
    # Risk management
    atr_period = 14
    stop_loss_pct = 0.01
    take_profit_pct = 0.01
    
    # Momentum thresholds
    price_change_1_threshold = 0.0005  # 0.05% in 1 period
    price_change_5_threshold = 0.007   # 0.7% in 5 periods
    volume_surge_multiplier = 1.5
    ma_drop_threshold = 0.95  # Exit if price < MA * 0.95
    
    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume
        
        # Moving average for trend
        self.ma = self.I(talib.SMA, close, timeperiod=self.ma_period)
        
        # ATR for risk management
        self.atr = self.I(talib.ATR, high, low, close, timeperiod=self.atr_period)
        
        # Volume average
        self.volume_avg = self.I(talib.SMA, volume, timeperiod=self.volume_lookback)
    
    def next(self):
        # Need enough data
        if len(self.data) < max(self.ma_period, self.atr_period):
            return
        
        # Check for NaN values
        if (np.isnan(self.ma[-1]) or np.isnan(self.atr[-1]) or 
            np.isnan(self.volume_avg[-1])):
            return
        
        current_price = self.data.Close[-1]
        
        # Calculate price changes
        if len(self.data) >= 2:
            price_change_1 = (current_price - self.data.Close[-2]) / self.data.Close[-2]
        else:
            price_change_1 = 0
        
        if len(self.data) >= 6:
            price_change_5 = (current_price - self.data.Close[-6]) / self.data.Close[-6]
        else:
            price_change_5 = 0
        
        # Volume explosion
        volume_surge = self.data.Volume[-1] > self.volume_avg[-1] * self.volume_surge_multiplier
        
        # Price above moving average
        price_above_ma = current_price > self.ma[-1]
        
        # Ultra-aggressive conditions
        any_momentum = (price_change_1 > self.price_change_1_threshold or 
                       price_change_5 > self.price_change_5_threshold)
        explosion_setup = volume_surge or price_above_ma
        
        # Buy signal - ultra aggressive
        buy_signal = (
            (any_momentum or explosion_setup) and
            not self.position
        )
        
        # Sell signal - major drop or below MA threshold
        sell_signal = (
            self.position and (
                current_price < self.ma[-1] * self.ma_drop_threshold or
                current_price < self.ma[-1]  # Below MA
            )
        )
        
        if buy_signal:
            # Position sizing: Use 25% of equity per trade
            position_size = 0.25
            
            # Risk management: ATR-based or percentage-based
            entry_price = current_price
            atr_value = self.atr[-1]
            
            # Use ATR if available, otherwise use percentage
            if not np.isnan(atr_value) and atr_value > 0:
                stop_loss = entry_price - (atr_value * 1.5)  # 1.5x ATR (tight)
                take_profit = entry_price + (atr_value * 2.5)  # 2.5x ATR
            else:
                stop_loss = entry_price * (1 - self.stop_loss_pct)
                take_profit = entry_price * (1 + self.take_profit_pct)
            
            # Ensure valid stop loss and take profit
            if stop_loss > 0 and take_profit > entry_price:
                self.buy(size=position_size, sl=stop_loss, tp=take_profit)
        
        elif sell_signal:
            self.position.close()

