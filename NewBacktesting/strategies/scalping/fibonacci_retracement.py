import numpy as np
import pandas as pd
from backtesting import Strategy

class FibonacciRetracementStrategy(Strategy):
    window = 20
    level1 = 0.618
    level2 = 0.382
    atr_period = 14
    atr_multiplier = 2.0
    rr_ratio = 2.0

    def init(self):
        self.recent_high = self.I(lambda x: pd.Series(x).rolling(self.window).max(), self.data.High)
        self.recent_low = self.I(lambda x: pd.Series(x).rolling(self.window).min(), self.data.Low)
        self.atr = self.I(lambda h, l, c: pd.Series(c).rolling(self.atr_period).std(), self.data.High, self.data.Low, self.data.Close)
    def next(self):
        if len(self.data) < 80:
            return
        price = self.data.Close[-1]
        high = self.recent_high[-1]
        low = self.recent_low[-1]
        if np.isnan(high) or np.isnan(low) or np.isnan(self.atr[-1]):
            return
        level_1 = high - (high - low) * self.level1
        level_2 = high - (high - low) * self.level2
        if not self.position:
            if price < level_1 or price < level_2:
                stop_loss = price - (self.atr[-1] * self.atr_multiplier)
                take_profit = price + (price - stop_loss) * self.rr_ratio
                self.buy(size=0.25, sl=stop_loss, tp=take_profit)
            elif price > high:
                stop_loss = price + (self.atr[-1] * self.atr_multiplier)
                take_profit = price - (stop_loss - price) * self.rr_ratio
                if take_profit < price < stop_loss:
                    self.sell(size=0.25, sl=stop_loss, tp=take_profit)
        elif self.position.is_long:
            if price > high:
                self.position.close()
        elif self.position.is_short:
            if price < level_1 or price < level_2:
                self.position.close() 