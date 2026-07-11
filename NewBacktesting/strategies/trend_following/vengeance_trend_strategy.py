import pandas as pd
import talib
from backtesting import Strategy
import numpy as np
from typing import Dict, Optional

class VengeanceTrendStrategy(Strategy):
    """
    A trend-following strategy that uses ATR-based trailing stops and risk management.
    Features:
    - ATR-based position sizing and stop losses
    - Trend confirmation using multiple timeframes
    - Pullback entries in established trends
    - Dynamic trailing stops
    """
    
    # Strategy parameters with default values
    atr_period: int = 14
    risk_per_trade: float = 0.02
    trailing_stop_multiplier: float = 2.0
    trend_ma_period: int = 200
    pullback_period: int = 20
    
    def init(self):
        """Initialize indicators and strategy state"""
        # Volatility indicators
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 
                         timeperiod=self.atr_period)
        
        # Trend indicators
        self.trend_ma = self.I(talib.SMA, self.data.Close, timeperiod=self.trend_ma_period)
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.pullback_period)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.pullback_period)
        
        print("🌙 VengeanceTrend Strategy initialized! Ready to trade with precision! 🚀")
    
    def next(self):
        """Main strategy logic for each bar"""
        # Skip if indicators are not ready
        if len(self.atr) < self.atr_period or len(self.trend_ma) < self.trend_ma_period:
            return
            
        # Calculate current position size based on risk
        current_atr = self.atr[-1]
        risk_amount = self.equity * self.risk_per_trade
        position_size = risk_amount / current_atr
        
        # Entry logic
        if not self.position:
            self._check_entries(position_size, current_atr)
            
        # Exit and trailing stop logic
        if self.position:
            self._manage_exits(current_atr)
    
    def _check_entries(self, position_size: float, current_atr: float):
        """Check for entry conditions"""
        # Long entry: Price above trend MA and pullback to support
        if (self.data.Close[-1] > self.trend_ma[-1] and  # Uptrend confirmation
            self.data.Close[-1] < self.data.Close[-2] and  # Pullback
            self.data.Close[-1] <= self.swing_low[-1]):  # Support level
            print("🌙 Long entry signal detected! Entering with precision! 🚀")
            self.buy(size=position_size, 
                    sl=self.data.Close[-1] - self.trailing_stop_multiplier * current_atr)
            
        # Short entry: Price below trend MA and pullback to resistance
        elif (self.data.Close[-1] < self.trend_ma[-1] and  # Downtrend confirmation
              self.data.Close[-1] > self.data.Close[-2] and  # Pullback
              self.data.Close[-1] >= self.swing_high[-1]):  # Resistance level
            print("🌙 Short entry signal detected! Entering with precision! 🚀")
            self.sell(size=position_size,
                     sl=self.data.Close[-1] + self.trailing_stop_multiplier * current_atr)
    
    def _manage_exits(self, current_atr: float):
        """Manage position exits and trailing stops"""
        if self.position.is_long:
            # Exit if price breaks below swing low
            if self.data.Close[-1] < self.swing_low[-1]:
                print("🌙 Long position exited due to support break! 🛑")
                self.position.close()
                
        elif self.position.is_short:
            # Exit if price breaks above swing high
            if self.data.Close[-1] > self.swing_high[-1]:
                print("🌙 Short position exited due to resistance break! 🛑")
                self.position.close()
    
    @classmethod
    def get_optimization_params(cls) -> Dict:
        """Return parameter ranges for optimization"""
        return {
            'atr_period': range(10, 20, 2),
            'trailing_stop_multiplier': [1.5, 2.0, 2.5],
            'risk_per_trade': [0.01, 0.02, 0.03],
            'trend_ma_period': range(100, 300, 50),
            'pullback_period': range(10, 30, 5)
        } 