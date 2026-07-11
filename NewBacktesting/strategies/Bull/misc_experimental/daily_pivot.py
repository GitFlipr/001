from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np

class DailyPivot(Strategy):
    def init(self):
        # Calculate daily pivot points
        self.pivot = self.I(self.calculate_pivot_points)
        
    def calculate_pivot_points(self, data):
        # Calculate pivot points for each day
        pivots = pd.Series(index=data.index, dtype=float)
        r1 = pd.Series(index=data.index, dtype=float)
        s1 = pd.Series(index=data.index, dtype=float)
        
        # Group by date
        for date, group in data.groupby(data.index.date):
            high = group.High.max()
            low = group.Low.min()
            close = group.Close.iloc[-1]
            
            # Calculate pivot point
            pivot = (high + low + close) / 3
            
            # Calculate R1 and S1
            r1_value = 2 * pivot - low
            s1_value = 2 * pivot - high
            
            # Assign values to the series
            pivots[group.index] = pivot
            r1[group.index] = r1_value
            s1[group.index] = s1_value
        
        return pivots, r1, s1
    
    def next(self):
        # Get current pivot points
        pivot, r1, s1 = self.pivot[-1]
        
        # Check if we have a position
        if not self.position:
            # Long entry conditions:
            # 1. Price breaks above pivot point
            # 2. Price is approaching R1
            if (self.data.Close[-1] > pivot and
                self.data.Close[-1] < r1):
                # Set stop loss below pivot
                stop_loss = pivot
                # Set take profit at R1
                take_profit = r1
                self.buy(sl=stop_loss, tp=take_profit)
            
            # Short entry conditions:
            # 1. Price breaks below pivot point
            # 2. Price is approaching S1
            elif (self.data.Close[-1] < pivot and
                  self.data.Close[-1] > s1):
                # Set stop loss above pivot
                stop_loss = pivot
                # Set take profit at S1
                take_profit = s1
                self.sell(sl=stop_loss, tp=take_profit)
        
        # Exit conditions
        else:
            # Long exit: Price reaches R1 or falls below pivot
            if self.position.is_long:
                if (self.data.Close[-1] >= r1 or
                    self.data.Close[-1] < pivot):
                    self.position.close()
            
            # Short exit: Price reaches S1 or rises above pivot
            elif self.position.is_short:
                if (self.data.Close[-1] <= s1 or
                    self.data.Close[-1] > pivot):
                    self.position.close()
