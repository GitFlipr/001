"""Kaufman adaptive MA vs slow SMA. From set_1/034."""
from backtesting import Strategy
import numpy as np
import talib


class AdaptiveMAStrategy(Strategy):
    kama_period = 10
    slow_period = 50

    def init(self):
        self.kama = self.I(talib.KAMA, self.data.Close, timeperiod=self.kama_period)
        self.slow = self.I(talib.SMA, self.data.Close, timeperiod=self.slow_period)

    def next(self):
        if len(self.data) < self.slow_period + 2:
            return
        if np.isnan(self.kama[-1]):
            return
        if not self.position:
            if self.kama[-1] > self.slow[-1]:
                self.buy()
            elif self.kama[-1] < self.slow[-1]:
                self.sell()
        else:
            if self.position.is_long and self.kama[-1] < self.slow[-1]:
                self.position.close()
            elif self.position.is_short and self.kama[-1] > self.slow[-1]:
                self.position.close()
