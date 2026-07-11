"""Retracement from rolling swing high/low; entries near 38.2–61.8%. From set_1/039."""
from backtesting import Strategy
import numpy as np
import talib


class FibRetracement(Strategy):
    lookback = 50
    lo_ratio = 0.382
    hi_ratio = 0.618

    def init(self):
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=self.lookback)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=self.lookback)

    def next(self):
        if len(self.data) < self.lookback + 1:
            return
        hi, lo = self.swing_high[-1], self.swing_low[-1]
        if np.isnan(hi) or hi <= lo:
            return
        r = hi - lo
        z_lo = lo + self.lo_ratio * r
        z_hi = lo + self.hi_ratio * r
        c = self.data.Close[-1]
        if not self.position:
            if z_lo <= c <= z_hi:
                self.buy()
        else:
            if self.position.is_long and (c >= hi - 0.1 * r or c <= lo):
                self.position.close()
