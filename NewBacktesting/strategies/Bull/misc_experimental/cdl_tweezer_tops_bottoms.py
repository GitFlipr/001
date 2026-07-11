"""
Tweezer Tops / Tweezer Bottoms reversal with RSI filter.

Signals:
- Long on CDLTWEEZERBOTTOM > 0 when RSI < rsi_oversold
- Short on CDLTWEEZERTOP < 0 / > 0 when RSI > rsi_overbought
- Exit on opposite pattern or RSI mean reversion past midline
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy


class CdlTweezerTopsBottoms(Strategy):
    rsi_period = 14
    rsi_oversold = 35
    rsi_overbought = 65
    rsi_mid = 50

    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.top = self.I(
            talib.CDLTWEEZERTOP,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )
        self.bot = self.I(
            talib.CDLTWEEZERBOTTOM,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )

    def next(self):
        if len(self.data) < self.rsi_period + 10:
            return
        if np.isnan(self.rsi[-1]):
            return
        rsi = float(self.rsi[-1])
        bull = float(self.bot[-1]) > 0 and rsi <= float(self.rsi_oversold)
        bear = (float(self.top[-1]) < 0 or float(self.top[-1]) > 0) and rsi >= float(
            self.rsi_overbought
        )

        if not self.position:
            if bull:
                self.buy()
            elif bear:
                self.sell()
            return

        if self.position.is_long:
            if bear or rsi >= float(self.rsi_mid):
                self.position.close()
        else:
            if bull or rsi <= float(self.rsi_mid):
                self.position.close()
