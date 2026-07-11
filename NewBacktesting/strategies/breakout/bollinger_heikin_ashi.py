"""
Bollinger Band Breakout + Smoothed Heikin Ashi - From 111.
BB 21, 2.7 std. Smoothed price (proxy for HA) - long when above upper BB + rising.
"""
import numpy as np
import pandas as pd
from backtesting import Strategy
import talib


class BollingerHeikinAshiStrategy(Strategy):
    """BB breakout + smoothed trend confirmation (Heikin Ashi proxy)."""

    bb_period = 21
    bb_std = 2.7
    smooth_period = 10

    def init(self):
        close = self.data.Close
        self.bb_upper, self.bb_mid, self.bb_lower = self.I(
            talib.BBANDS, close, self.bb_period, self.bb_std, self.bb_std
        )
        self.smooth = self.I(lambda c: np.asarray(pd.Series(c).ewm(span=self.smooth_period, adjust=False).mean()), close)

    def next(self):
        if len(self.data) < self.bb_period + self.smooth_period + 5:
            return
        if np.isnan(self.bb_upper[-1]) or np.isnan(self.smooth[-1]):
            return

        price = self.data.Close[-1]
        sm = self.smooth[-1]
        sm_prev = self.smooth[-2] if len(self.data) >= 2 else sm
        green = sm > sm_prev
        red = sm < sm_prev
        above_upper = price > self.bb_upper[-1]
        below_lower = price < self.bb_lower[-1]

        if not self.position:
            if above_upper and green:
                self.buy()
            elif below_lower and red:
                self.sell()
        else:
            if self.position.is_long and (below_lower or red):
                self.position.close()
            elif self.position.is_short and (above_upper or green):
                self.position.close()
