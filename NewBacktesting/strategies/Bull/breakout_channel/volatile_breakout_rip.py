"""Volatile regime: volatility expansion + channel break (TA-Lib)."""

import numpy as np
import talib
from backtesting import Strategy


class VolatileBreakoutRip(Strategy):
    atr_period = 14
    atr_ema_period = 50
    atr_exp_mult = 1.15

    donchian_len = 20
    stop_atr_mult = 2.2

    def init(self):
        c = self.data.Close
        h = self.data.High
        l = self.data.Low
        self.atr = self.I(talib.ATR, h, l, c, timeperiod=self.atr_period)
        self.atr_ema = self.I(talib.EMA, self.atr, timeperiod=self.atr_ema_period)
        self.hh = self.I(talib.MAX, h, timeperiod=self.donchian_len)
        self.ll = self.I(talib.MIN, l, timeperiod=self.donchian_len)

    def next(self):
        need = max(self.atr_period, self.atr_ema_period, self.donchian_len) + 5
        if len(self.data) < need:
            return
        c = float(self.data.Close[-1])
        atr = float(self.atr[-1])
        atr_ema = float(self.atr_ema[-1])
        hh = float(self.hh[-2])  # prior channel
        ll = float(self.ll[-2])
        if any(np.isnan(x) for x in (atr, atr_ema, hh, ll)) or atr <= 0 or atr_ema <= 0:
            return

        volatile = atr >= atr_ema * self.atr_exp_mult

        if not self.position:
            if volatile and c > hh:
                sl = c - self.stop_atr_mult * atr
                if sl < c:
                    self.buy(sl=sl)
            elif volatile and c < ll:
                sl = c + self.stop_atr_mult * atr
                if c < sl:
                    self.sell(sl=sl)
        else:
            # Exit if volatility compresses (stop trading chop).
            if not volatile:
                self.position.close()

