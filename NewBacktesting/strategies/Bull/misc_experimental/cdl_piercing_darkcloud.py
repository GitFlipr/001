"""
Piercing Line / Dark Cloud Cover reversal with SMA bias.

Signals:
- Long on CDLPIERCING > 0 when Close > SMA(bias_period)
- Short on CDLDARKCLOUDCOVER > 0/negative (depends) when Close < SMA(bias_period)
- Exit on opposite signal or bias flip
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy


class CdlPiercingDarkCloud(Strategy):
    bias_period = 100
    penetration = 0.5

    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.bias_period)
        self.piercing = self.I(
            talib.CDLPIERCING,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )
        self.dark = self.I(
            talib.CDLDARKCLOUDCOVER,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
            penetration=self.penetration,
        )

    def next(self):
        if len(self.data) < self.bias_period + 10:
            return
        if np.isnan(self.sma[-1]):
            return
        close = float(self.data.Close[-1])
        sma = float(self.sma[-1])
        bull = float(self.piercing[-1]) > 0
        bear = float(self.dark[-1]) < 0 or float(self.dark[-1]) > 0
        up = close > sma
        dn = close < sma

        if not self.position:
            if bull and up:
                self.buy()
            elif bear and dn:
                self.sell()
            return

        if self.position.is_long and (bear or dn):
            self.position.close()
        elif self.position.is_short and (bull or up):
            self.position.close()
