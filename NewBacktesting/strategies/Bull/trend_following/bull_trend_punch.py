"""Bull regime hard hitter: EMA stack + ADX + momentum (TA-Lib)."""

import numpy as np
import talib
from backtesting import Strategy


class BullTrendPunch(Strategy):
    ema_fast = 20
    ema_slow = 100
    adx_period = 14
    adx_min = 18.0
    roc_period = 10
    roc_min = 0.6  # percent

    atr_period = 14
    atr_stop_mult = 2.2

    def init(self):
        c = self.data.Close
        h = self.data.High
        l = self.data.Low
        self.ema_f = self.I(talib.EMA, c, timeperiod=self.ema_fast)
        self.ema_s = self.I(talib.EMA, c, timeperiod=self.ema_slow)
        self.adx = self.I(talib.ADX, h, l, c, timeperiod=self.adx_period)
        self.roc = self.I(talib.ROC, c, timeperiod=self.roc_period)
        self.atr = self.I(talib.ATR, h, l, c, timeperiod=self.atr_period)

    def next(self):
        need = max(self.ema_slow, self.adx_period, self.roc_period, self.atr_period) + 5
        if len(self.data) < need:
            return
        c = float(self.data.Close[-1])
        ef = float(self.ema_f[-1])
        es = float(self.ema_s[-1])
        adx = float(self.adx[-1])
        roc = float(self.roc[-1])
        atr = float(self.atr[-1])
        if any(np.isnan(x) for x in (ef, es, adx, roc, atr)) or atr <= 0:
            return

        trend = ef > es and c > es and adx >= self.adx_min
        punch = roc >= self.roc_min

        if not self.position:
            if trend and punch:
                sl = c - self.atr_stop_mult * atr
                if sl < c:
                    self.buy(sl=sl)
        else:
            if self.position.is_long and (ef < es or roc < 0):
                self.position.close()

