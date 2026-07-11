"""STARC: CMA 6 ± 2*ATR; reversal at band. From set_2/079."""
import numpy as np
import talib
from backtesting import Strategy


class StollerBands(Strategy):
    cma_period = 6
    atr_period = 15
    atr_mult = 2.0

    def init(self):
        self.cma = self.I(talib.SMA, self.data.Close, timeperiod=self.cma_period)
        self.atr = self.I(
            talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period
        )

    def next(self):
        if len(self.data) < max(self.cma_period, self.atr_period) + 2:
            return
        if np.isnan(self.atr[-1]):
            return
        up = self.cma[-1] + self.atr_mult * self.atr[-1]
        lo = self.cma[-1] - self.atr_mult * self.atr[-1]
        c, o, h, l_ = self.data.Close[-1], self.data.Open[-1], self.data.High[-1], self.data.Low[-1]
        rng = max(h - l_, 1e-12)
        hammer = (c > o) and (c - o) / rng < 0.35 and (min(o, c) - l_) > 2 * abs(c - o)
        star = (c < o) and (o - c) / rng < 0.35 and (h - max(o, c)) > 2 * abs(o - c)
        if not self.position:
            if c < lo and hammer:
                self.buy()
            elif c > up and star:
                self.sell()
        else:
            if self.position.is_long and c >= self.cma[-1]:
                self.position.close()
            elif self.position.is_short and c <= self.cma[-1]:
                self.position.close()
