"""Range / mean reversion when trend strength (ADX) is low."""

import numpy as np
from backtesting import Strategy
import talib


class RangeTradingStrategy(Strategy):
    adx_period = 14
    adx_max = 25
    bb_period = 20
    bb_std = 2.0

    def init(self):
        h, l, c = self.data.High, self.data.Low, self.data.Close
        self.adx = self.I(talib.ADX, h, l, c, timeperiod=self.adx_period)
        self.upper, self.mid, self.lower = self.I(
            talib.BBANDS, c, timeperiod=self.bb_period, nbdevup=self.bb_std, nbdevdn=self.bb_std, matype=0
        )

    def next(self):
        if len(self.data) < self.bb_period + 2:
            return
        if np.isnan(self.adx[-1]) or np.isnan(self.lower[-1]):
            return

        ranging = self.adx[-1] < self.adx_max
        at_lower = self.data.Close[-1] <= self.lower[-1] * 1.002
        at_upper = self.data.Close[-1] >= self.upper[-1] * 0.998

        if ranging and at_lower and not self.position:
            self.buy()
        elif self.position and ranging and at_upper:
            self.position.close()
