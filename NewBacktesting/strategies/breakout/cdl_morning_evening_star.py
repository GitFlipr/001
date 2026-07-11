"""
Morning Star / Evening Star reversal with simple confirmation.

Signals:
- Long on CDLMORNINGSTAR > 0 with confirmation close above SMA(confirm_period)
- Short on CDLEVENINGSTAR < 0 (TA-Lib typically negative) with confirmation close below SMA(confirm_period)
- Exit on opposite pattern or confirmation flipping
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy


class CdlMorningEveningStar(Strategy):
    confirm_period = 50
    penetration = 0.3  # TA-Lib default style uses 0.3 often in examples

    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.confirm_period)
        self.morning = self.I(
            talib.CDLMORNINGSTAR,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
            penetration=self.penetration,
        )
        self.evening = self.I(
            talib.CDLEVENINGSTAR,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
            penetration=self.penetration,
        )

    def next(self):
        if len(self.data) < self.confirm_period + 10:
            return
        if np.isnan(self.sma[-1]):
            return
        close = float(self.data.Close[-1])
        sma = float(self.sma[-1])
        bull = float(self.morning[-1]) > 0
        bear = float(self.evening[-1]) < 0 or float(self.evening[-1]) > 0  # depending on build

        if not self.position:
            if bull and close > sma:
                self.buy()
            elif bear and close < sma:
                self.sell()
            return

        if self.position.is_long:
            if bear or close < sma:
                self.position.close()
        else:
            if bull or close > sma:
                self.position.close()
