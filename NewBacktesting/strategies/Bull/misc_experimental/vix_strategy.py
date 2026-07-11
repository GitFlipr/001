from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np

class VIXStrategy(Strategy):
    # Strategy parameters
    vix_ma_period = 20
    vix_threshold = 30
    atr_period = 14
    risk_per_trade = 0.02     # 2% risk per trade
    
    def init(self):
        # Initialize indicators
        self.vix_ma = self.I(self.vix_ma_period)
        self.atr = self.I(self.atr_period)
        
        # Track trade information
        self.trade_size = None
        self.stop_loss = None
        self.entry_price = None
    
    def next(self):
        # Skip if we don't have enough data
        if len(self.data) < self.vix_ma_period:
            return
            
        # Calculate current position
        current_position = self.position.size
        
        # Calculate VIX conditions
        vix_above_threshold = self.data.VIX[-1] > self.vix_threshold
        vix_rising = self.data.VIX[-1] > self.vix_ma[-1]
        
        # Calculate position size based on ATR and risk
        if self.trade_size is None:
            atr_value = self.atr[-1]
            risk_amount = self.equity * self.risk_per_trade
            self.trade_size = risk_amount / atr_value
        
        # Entry conditions
        if current_position == 0:
            # Short entry when VIX is high and rising
            if vix_above_threshold and vix_rising:
                self.sell(size=self.trade_size)
                self.entry_price = self.data.Close[-1]
                self.stop_loss = self.entry_price + (atr_value * 2.0)
            
            # Long entry when VIX is low and falling
            elif not vix_above_threshold and not vix_rising:
                self.buy(size=self.trade_size)
                self.entry_price = self.data.Close[-1]
                self.stop_loss = self.entry_price - (atr_value * 2.0)
        
        # Manage existing positions
        elif current_position > 0:  # Long position
            # Update stop loss if price moves in our favor
            if self.data.Close[-1] > self.entry_price:
                new_stop = self.data.Close[-1] - (self.atr[-1] * 1.5)
                self.stop_loss = max(self.stop_loss, new_stop)
            
            # Check for exit conditions
            if self.data.Close[-1] < self.stop_loss or vix_above_threshold:
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
            if self.data.Close[-1] > self.stop_loss or not vix_above_threshold:
                self.position.close()
                self.trade_size = None
                self.stop_loss = None
                self.entry_price = None
