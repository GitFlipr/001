"""
Bullish/Bearish Engulfing with trend filter.

Signals:
- Go long on bullish engulfing when Close > SMA(trend_period)
- Go short on bearish engulfing when Close < SMA(trend_period)
- Exit on opposite signal or SMA cross back against position
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy


class CdlEngulfingTrendFilter(Strategy):
    trend_period = 200

    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.trend_period)
        self.engulf = self.I(
            talib.CDLENGULFING,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )

    def next(self):
        if len(self.data) < self.trend_period + 5:
            return
        if np.isnan(self.sma[-1]):
            return
        sig = float(self.engulf[-1])
        bull = sig > 0
        bear = sig < 0
        up = float(self.data.Close[-1]) > float(self.sma[-1])
        dn = float(self.data.Close[-1]) < float(self.sma[-1])

        if not self.position:
            if bull and up:
                self.buy()
            elif bear and dn:
                self.sell()
            return

        if self.position.is_long:
            if bear or dn:
                self.position.close()
        else:
            if bull or up:
                self.position.close()
