from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

class VolumeBreakout(Strategy):
    # Strategy parameters
    consolidation_period = 20  # Lookback period for consolidation
    volume_multiplier = 2.0    # Volume spike threshold
    atr_period = 14
    risk_per_trade = 0.02     # 2% risk per trade
    
    def init(self):
        # Initialize indicators
        self.volume_sma = self.I(self.consolidation_period)
        self.atr = self.I(self.atr_period)
        
        # Calculate price range for consolidation
        self.high_range = self.data.High.rolling(self.consolidation_period).max()
        self.low_range = self.data.Low.rolling(self.consolidation_period).min()
        
        # Track trade information
        self.trade_size = None
        self.stop_loss = None
        self.entry_price = None
    
    def next(self):
        # Skip if we don't have enough data
        if len(self.data) < self.consolidation_period:
            return
            
        # Calculate current position
        current_position = self.position.size
        
        # Calculate volume spike
        volume_spike = self.data.Volume[-1] > (self.volume_sma[-1] * self.volume_multiplier)
        
        # Calculate price range
        price_range = self.high_range[-1] - self.low_range[-1]
        range_breakout = (self.data.Close[-1] > self.high_range[-1]) or (self.data.Close[-1] < self.low_range[-1])
        
        # Calculate position size based on ATR and risk
        if self.trade_size is None:
            atr_value = self.atr[-1]
            risk_amount = self.equity * self.risk_per_trade
            self.trade_size = risk_amount / atr_value
        
        # Entry conditions
        if current_position == 0 and volume_spike and range_breakout:
            # Breakout to the upside
            if self.data.Close[-1] > self.high_range[-1]:
                self.buy(size=self.trade_size)
                self.entry_price = self.data.Close[-1]
                self.stop_loss = self.entry_price - (atr_value * 1.5)
            
            # Breakout to the downside
            elif self.data.Close[-1] < self.low_range[-1]:
                self.sell(size=self.trade_size)
                self.entry_price = self.data.Close[-1]
                self.stop_loss = self.entry_price + (atr_value * 1.5)
        
        # Manage existing positions
        elif current_position > 0:  # Long position
            # Update stop loss if price moves in our favor
            if self.data.Close[-1] > self.entry_price:
                new_stop = self.data.Close[-1] - (self.atr[-1] * 1.5)
                self.stop_loss = max(self.stop_loss, new_stop)
            
            # Check for exit conditions
            if self.data.Close[-1] < self.stop_loss:
                self.position.close()
                self.trade_size = None
                self.stop_loss = None
                self.entry_price = None
        
        elif current_position < 0:  # Short position
            # Update stop loss if price moves in our favor
            if self.data.Close[-1] < self.entry_price:
                new_stop = self.data.Close[-1] + (self.atr[-1] * 1.5)
                self.stop_loss = min(self.stop_loss, new_stop)
            
            # Check for exit conditions
            if self.data.Close[-1] > self.stop_loss:
                self.position.close()
                self.trade_size = None
                self.stop_loss = None
                self.entry_price = None
