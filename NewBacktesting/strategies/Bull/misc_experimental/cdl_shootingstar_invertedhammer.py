"""
Shooting Star / Inverted Hammer with ATR stop.

Signals:
- Long on CDLINVERTEDHAMMER > 0
- Short on CDLSHOOTINGSTAR < 0 / > 0 (depends) with basic trend check (Close < SMA)
- Exit on opposite pattern or stop
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy


class CdlShootingStarInvertedHammer(Strategy):
    trend_period = 150
    atr_period = 14
    atr_mult = 2.0

    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.trend_period)
        self.atr = self.I(
            talib.ATR,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.atr_period,
        )
        self.inv = self.I(
            talib.CDLINVERTEDHAMMER,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )
        self.shoot = self.I(
            talib.CDLSHOOTINGSTAR,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )

    def next(self):
        if len(self.data) < max(self.trend_period, self.atr_period) + 10:
            return
        if np.isnan(self.atr[-1]) or np.isnan(self.sma[-1]):
            return

        close = float(self.data.Close[-1])
        atr = float(self.atr[-1])
        sma = float(self.sma[-1])

        bull = float(self.inv[-1]) > 0 and close > sma
        bear = (float(self.shoot[-1]) < 0 or float(self.shoot[-1]) > 0) and close < sma

        if not self.position:
            if bull:
                self.buy(sl=close - self.atr_mult * atr)
            elif bear:
                self.sell(sl=close + self.atr_mult * atr)
            return

        if self.position.is_long:
            if bear or close < sma:
                self.position.close()
        else:
            if bull or close > sma:
                self.position.close()
