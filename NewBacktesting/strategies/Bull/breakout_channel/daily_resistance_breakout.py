from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib


def _rolling_max(arr, window):
    return pd.Series(arr).rolling(window).max().to_numpy()


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


class DailyResistanceBreakout(Strategy):
    # Define the strategy parameters
    resistance_lookback = 20  # Number of days to look back for resistance
    atr_period = 14  # ATR period for stop loss
    atr_multiplier = 2.0  # ATR multiplier for stop loss
    
    def init(self):
        # Calculate ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # Calculate recent highs for resistance levels
        self.recent_highs = self.I(_rolling_max, self.data.High, self.resistance_lookback)
        
        # Calculate volume SMA for confirmation
        self.volume_sma = self.I(_rolling_mean, self.data.Volume, 20)
        
        # Store resistance levels
        self.resistance_levels = []
    
    def next(self):
        # Update resistance levels
        current_high = self.data.High[-1]
        if current_high > self.recent_highs[-2]:
            self.resistance_levels.append(current_high)
            # Keep only the last 5 resistance levels
            self.resistance_levels = self.resistance_levels[-5:]
        
        # Check if we have a position
        if not self.position:
            # Find the nearest resistance level above current price
            nearest_resistance = None
            for level in sorted(self.resistance_levels):
                if level > self.data.Close[-1]:
                    nearest_resistance = level
                    break
            
            if nearest_resistance:
                # Long entry conditions:
                # 1. Price breaks above resistance
                # 2. Volume is above average
                if (self.data.Close[-1] > nearest_resistance and
                    self.data.Volume[-1] > self.volume_sma[-1]):
                    # Set stop loss using ATR
                    stop_loss = self.data.Close[-1] - (self.atr[-1] * self.atr_multiplier)
                    # Set take profit at next resistance level
                    next_resistance = None
                    for level in sorted(self.resistance_levels):
                        if level > nearest_resistance:
                            next_resistance = level
                            break
                    take_profit = next_resistance if next_resistance else self.data.Close[-1] * 1.1
                    self.buy(sl=stop_loss, tp=take_profit)
        
        # Exit conditions managed via initial sl=/tp= on orders
        else:
            pass
