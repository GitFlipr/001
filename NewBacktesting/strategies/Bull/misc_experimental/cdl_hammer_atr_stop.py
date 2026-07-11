"""
Hammer / Hanging Man reversal with ATR stop.

Uses TA-Lib:
- CDLHAMMER (bullish)
- CDLHANGINGMAN (bearish)

Signals:
- Long on hammer, short on hanging man
- Optional regime filter via SMA(trend_period)
- Exit via ATR-based stop or opposite pattern
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy


class CdlHammerAtrStop(Strategy):
    trend_period = 100
    atr_period = 14
    atr_mult = 2.5
    use_trend_filter = True

    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.trend_period)
        self.atr = self.I(
            talib.ATR,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.atr_period,
        )
        self.hammer = self.I(
            talib.CDLHAMMER,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )
        self.hanging = self.I(
            talib.CDLHANGINGMAN,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )

    def next(self):
        if len(self.data) < max(self.trend_period, self.atr_period) + 5:
            return
        if np.isnan(self.atr[-1]):
            return

        close = float(self.data.Close[-1])
        atr = float(self.atr[-1])
        long_ok = True
        short_ok = True
        if self.use_trend_filter:
            if np.isnan(self.sma[-1]):
                return
            long_ok = close > float(self.sma[-1])
            short_ok = close < float(self.sma[-1])

        bull = float(self.hammer[-1]) > 0
        bear = float(self.hanging[-1]) < 0 or float(self.hanging[-1]) > 0  # TA-Lib uses +100

        if not self.position:
            if bull and long_ok:
                self.buy(sl=close - self.atr_mult * atr)
            elif bear and short_ok:
                self.sell(sl=close + self.atr_mult * atr)
            return

        if self.position.is_long:
            if bear:
                self.position.close()
        else:
            if bull:
                self.position.close()
