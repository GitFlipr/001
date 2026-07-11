from base_strategy import BaseStrategy
import numpy as np

class RSIDivergenceStrategy(BaseStrategy):
    """RSI Divergence strategy with support/resistance confirmation"""
    
    # Strategy parameters
    rsi_period = 14
    sr_period = 20  # Period for support/resistance calculation
    lookback = 5    # Lookback period for divergence detection
    atr_period = 14
    
    # Risk management parameters
    risk_per_trade = 0.02  # 2% risk per trade
    atr_stop_multiplier = 2.0  # Stop loss at 2x ATR
    
    def init(self):
        """Initialize strategy indicators"""
        # Calculate RSI
        self.rsi = self.calculate_rsi(self.rsi_period)
        
        # Calculate support and resistance levels
        self.support, self.resistance = self.calculate_support_resistance(self.sr_period)
        
        # Calculate ATR for position sizing and stops
        self.atr = self.calculate_atr(self.atr_period)
    
    def next(self):
        """Implement trading logic for each bar"""
        if len(self.data) < max(self.rsi_period, self.sr_period):
            return
            
        price = self.data.Close[-1]
        
        # Detect RSI divergence
        bullish_div, bearish_div = self.detect_divergence(self.rsi, self.lookback)
        
        # Calculate position size and stop distance
        stop_distance = self.atr[-1] * self.atr_stop_multiplier
        position_size = self.calculate_position_size(self.equity, price, self.risk_per_trade)
        
        if not self.position:  # If not in a position
            # Bullish divergence near support
            if bullish_div and price <= self.support[-1] * 1.02:  # Within 2% of support
                sl = price - stop_distance
                tp = price + (stop_distance * 2)  # 1:2 risk-reward
                self.buy(size=position_size, sl=sl, tp=tp)
                
            # Bearish divergence near resistance    
            elif bearish_div and price >= self.resistance[-1] * 0.98:  # Within 2% of resistance
                sl = price + stop_distance
                tp = price - (stop_distance * 2)  # 1:2 risk-reward
                self.sell(size=position_size, sl=sl, tp=tp)
                
        else:  # If in a position
            # Exit long position on bearish divergence or resistance break
            if self.position.is_long:
                if bearish_div or price >= self.resistance[-1]:
                    self.position.close()
                    
            # Exit short position on bullish divergence or support break
            elif self.position.is_short:
                if bullish_div or price <= self.support[-1]:
                    self.position.close() 