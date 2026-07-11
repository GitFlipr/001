"""Bear regime hard hitter: sell rallies into EMA with RSI overbought + ADX (TA-Lib)."""

import numpy as np
import talib
from backtesting import Strategy


class BearRallyFade(Strategy):
    ema_fast = 20
    ema_slow = 100
    adx_period = 14
    adx_min = 16.0

    rsi_period = 14
    rsi_ob = 60

    atr_period = 14
    stop_atr_mult = 2.0
    take_atr_mult = 1.6

    def init(self):
        c = self.data.Close
        h = self.data.High
        l = self.data.Low
        self.ema_f = self.I(talib.EMA, c, timeperiod=self.ema_fast)
        self.ema_s = self.I(talib.EMA, c, timeperiod=self.ema_slow)
        self.adx = self.I(talib.ADX, h, l, c, timeperiod=self.adx_period)
        self.rsi = self.I(talib.RSI, c, timeperiod=self.rsi_period)
        self.atr = self.I(talib.ATR, h, l, c, timeperiod=self.atr_period)

    def next(self):
        need = max(self.ema_slow, self.adx_period, self.rsi_period, self.atr_period) + 5
        if len(self.data) < need:
            return
        c = float(self.data.Close[-1])
        ef = float(self.ema_f[-1])
        es = float(self.ema_s[-1])
        adx = float(self.adx[-1])
        rsi = float(self.rsi[-1])
        atr = float(self.atr[-1])
        if any(np.isnan(x) for x in (ef, es, adx, rsi, atr)) or atr <= 0:
            return

        bear = ef < es and c < es and adx >= self.adx_min
        rally = c >= ef  # pullback to fast EMA
        overbought = rsi >= self.rsi_ob

        if not self.position:
            if bear and rally and overbought:
                sl = c + self.stop_atr_mult * atr
                tp = c - self.take_atr_mult * atr
                if tp < c < sl:
                    self.sell(sl=sl, tp=tp)
        else:
            if self.position.is_short and (c > es or rsi < 45):
                self.position.close()

