"""
Short-Term MA Crossover with ADX - From 106.
10 x 30 MA + ADX > 25. Long when fast > slow and ADX > 25.
"""
import numpy as np
from backtesting import Strategy
import talib


class MACrossoverADXStrategy(Strategy):
    """10 x 30 MA + ADX filter. Fast trend following."""

    fast_period = 10
    slow_period = 30
    adx_period = 14
    adx_threshold = 25

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        self.ema10 = self.I(talib.EMA, close, timeperiod=self.fast_period)
        self.ema30 = self.I(talib.EMA, close, timeperiod=self.slow_period)
        self.adx = self.I(talib.ADX, high, low, close, timeperiod=self.adx_period)

    def next(self):
        if len(self.data) < self.slow_period + self.adx_period + 5:
            return
        if np.isnan(self.adx[-1]):
            return

        trend_strong = self.adx[-1] > self.adx_threshold
        bullish = self.ema10[-1] > self.ema30[-1]
        bearish = self.ema10[-1] < self.ema30[-1]

        if not self.position:
            if bullish and trend_strong:
                self.buy()
            elif bearish and trend_strong:
                self.sell()
        else:
            cross_down = self.ema10[-1] < self.ema30[-1] and (len(self.data) < 2 or self.ema10[-2] >= self.ema30[-2])
            cross_up = self.ema10[-1] > self.ema30[-1] and (len(self.data) < 2 or self.ema10[-2] <= self.ema30[-2])
            if self.position.is_long and (cross_down or self.adx[-1] < 20):
                self.position.close()
            elif self.position.is_short and (cross_up or self.adx[-1] < 20):
                self.position.close()
