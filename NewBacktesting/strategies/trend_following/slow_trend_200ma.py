"""
200-Day Moving Average Long Strategy - From 109/102.
Long when price closes above 200-day MA, exit when below.
"""
import numpy as np
from backtesting import Strategy
import talib


class SlowTrend200MAStrategy(Strategy):
    """200-day MA long only. Enter above, exit below."""

    ma_period = 200

    def init(self):
        close = self.data.Close
        self.ma200 = self.I(talib.SMA, close, timeperiod=self.ma_period)

    def next(self):
        if len(self.data) < self.ma_period + 5:
            return
        if np.isnan(self.ma200[-1]):
            return

        price = self.data.Close[-1]
        if not self.position:
            if price > self.ma200[-1]:
                self.buy()
        else:
            if price < self.ma200[-1]:
                self.position.close()
