"""Proxy support = rolling low; buy shallow dips with RSI filter."""

import numpy as np
from backtesting import Strategy
import talib


class SupportBounceStrategy(Strategy):
    support_lookback = 20
    proximity_pct = 0.005
    rsi_period = 14
    rsi_max = 45

    def init(self):
        self.support = self.I(talib.MIN, self.data.Low, timeperiod=self.support_lookback)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)

    def next(self):
        if len(self.data) < self.support_lookback + 1:
            return
        if np.isnan(self.support[-1]) or np.isnan(self.rsi[-1]):
            return

        s = self.support[-1]
        lo = s * (1 - self.proximity_pct)
        hi = s * (1 + self.proximity_pct)
        near_support = lo <= self.data.Low[-1] <= hi or self.data.Close[-1] <= hi
        bounce = self.data.Close[-1] > self.data.Open[-1]

        if near_support and bounce and self.rsi[-1] < self.rsi_max and not self.position:
            self.buy()
        elif self.position and self.data.Close[-1] < s * 0.99:
            self.position.close()
