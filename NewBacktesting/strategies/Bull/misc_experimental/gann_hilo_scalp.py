"""Gann HiLo Activator-style scalper (TA-Lib).

Classic "Gann HiLo Activator" uses moving average of highs/lows; trend flips on close crossing.
"""

import numpy as np
import talib
from backtesting import Strategy


class GannHiLoScalp(Strategy):
    hilo_period = 10
    atr_period = 14
    stop_atr_mult = 1.6

    def init(self):
        h = self.data.High
        l = self.data.Low
        c = self.data.Close
        self.hi_ma = self.I(talib.SMA, h, timeperiod=self.hilo_period)
        self.lo_ma = self.I(talib.SMA, l, timeperiod=self.hilo_period)
        self.atr = self.I(talib.ATR, h, l, c, timeperiod=self.atr_period)

    def next(self):
        need = max(self.hilo_period, self.atr_period) + 5
        if len(self.data) < need:
            return
        c = float(self.data.Close[-1])
        hi = float(self.hi_ma[-1])
        lo = float(self.lo_ma[-1])
        atr = float(self.atr[-1])
        if any(np.isnan(x) for x in (hi, lo, atr)) or atr <= 0:
            return

        # Flip logic: close above high-MA => bull; below low-MA => bear.
        bull = c > hi
        bear = c < lo

        if not self.position:
            if bull:
                sl = c - self.stop_atr_mult * atr
                if sl < c:
                    self.buy(sl=sl)
            elif bear:
                sl = c + self.stop_atr_mult * atr
                if c < sl:
                    self.sell(sl=sl)
        else:
            if self.position.is_long and bear:
                self.position.close()
            elif self.position.is_short and bull:
                self.position.close()

