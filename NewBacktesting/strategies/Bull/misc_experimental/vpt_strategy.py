from base_strategy import BaseStrategy
import talib
import numpy as np

class VPTStrategy(BaseStrategy):
    """Volume Price Trend strategy with moving average confirmation"""
    
    # Strategy parameters
    vpt_ma_period = 20    # VPT moving average period
    price_ma_period = 50  # Price moving average period
    atr_period = 14
    
    # Risk management parameters
    risk_per_trade = 0.02  # 2% risk per trade
    atr_stop_multiplier = 2.0  # Stop loss at 2x ATR
    
    def init(self):
        """Initialize strategy indicators"""
        # Calculate VPT
        self.vpt = self.calculate_vpt()
        
        # Calculate VPT moving average
        self.vpt_ma = self.I(talib.SMA, self.vpt, self.vpt_ma_period)
        
        # Calculate price moving average
        self.price_ma = self.I(talib.SMA, self.data.Close, self.price_ma_period)
        
        # Calculate ATR for position sizing and stops
        self.atr = self.calculate_atr(self.atr_period)
        
        # Track VPT divergence
        self.bullish_div, self.bearish_div = False, False
    
    def next(self):
        """Implement trading logic for each bar"""
        if len(self.data) < max(self.vpt_ma_period, self.price_ma_period):
            return
            
        price = self.data.Close[-1]
        
        # Detect VPT divergence
        self.bullish_div, self.bearish_div = self.detect_divergence(self.vpt, lookback=5)
        
        # Calculate position size and stop distance
        stop_distance = self.atr[-1] * self.atr_stop_multiplier
        position_size = self.calculate_position_size(self.equity, price, self.risk_per_trade)
        
        # VPT trend signals
        vpt_uptrend = self.vpt[-1] > self.vpt_ma[-1]
        vpt_downtrend = self.vpt[-1] < self.vpt_ma[-1]
        
        # Price trend signals
        price_uptrend = price > self.price_ma[-1]
        price_downtrend = price < self.price_ma[-1]
        
        if not self.position:  # If not in a position
            # Bullish conditions
            if (vpt_uptrend and price_uptrend) or self.bullish_div:
                sl = price - stop_distance
                tp = price + (stop_distance * 2)  # 1:2 risk-reward
                self.buy(size=position_size, sl=sl, tp=tp)
                
            # Bearish conditions    
            elif (vpt_downtrend and price_downtrend) or self.bearish_div:
                sl = price + stop_distance
                tp = price - (stop_distance * 2)  # 1:2 risk-reward
                self.sell(size=position_size, sl=sl, tp=tp)
                
        else:  # If in a position
            # Exit long position
            if self.position.is_long:
                if vpt_downtrend or self.bearish_div:
                    self.position.close()
                    
            # Exit short position
            elif self.position.is_short:
                if vpt_uptrend or self.bullish_div:
                    self.position.close() 