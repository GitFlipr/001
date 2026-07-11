"""
Silver-bullet style displacement: after a tight micro-range, trade the breakout.

`session_bars` groups bars into synthetic sessions when the backtest index has no clock.
"""

import numpy as np
from backtesting import Strategy
import talib


class SilverBulletAMSessionStrategy(Strategy):
    session_bars = 96
    micro_range = 4
    min_body_atr = 0.3
    atr_period = 14

    def init(self):
        h, l, c = self.data.High, self.data.Low, self.data.Close
        self.atr = self.I(talib.ATR, h, l, c, timeperiod=self.atr_period)
    def next(self):
        if len(self.data) < 80:
            return
        i = len(self.data) - 1
        if i < self.micro_range + 3:
            return

        pos_in_session = i % self.session_bars
        if pos_in_session < self.micro_range + 2:
            return

        seg_hi = max(self.data.High[i - self.micro_range : i])
        seg_lo = min(self.data.Low[i - self.micro_range : i])
        seg_rng = seg_hi - seg_lo
        atr = self.atr[-1]
        if np.isnan(atr) or atr <= 0:
            return

        tight = seg_rng < atr * 0.6
        body = abs(self.data.Close[-1] - self.data.Open[-1])
        strong = body > atr * self.min_body_atr

        if tight and strong and self.data.Close[-1] > seg_hi and not self.position:
            self.buy()
        elif self.position and self.data.Close[-1] < seg_lo:
            self.position.close()
