"""
Inside Three Up / Inside Three Down (three-candle continuation) with ATR trail.

Signals:
- Long on CDLINSIDE3 > 0
- Short on CDLINSIDE3 < 0
- Exit uses a lightweight ATR trailing stop updated each bar (also exit on opposite signal)
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy


class CdlInside3WithAtrTrail(Strategy):
    atr_period = 14
    atr_mult = 2.5

    def init(self):
        self.atr = self.I(
            talib.ATR,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.atr_period,
        )
        self.inside3 = self.I(
            talib.CDLINSIDE3,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )
        self._trail = None  # type: float | None

    def next(self):
        if len(self.data) < self.atr_period + 10:
            return
        if np.isnan(self.atr[-1]):
            return

        close = float(self.data.Close[-1])
        atr = float(self.atr[-1])
        sig = float(self.inside3[-1])
        bull = sig > 0
        bear = sig < 0

        if not self.position:
            self._trail = None
            if bull:
                self.buy()
                self._trail = close - self.atr_mult * atr
            elif bear:
                self.sell()
                self._trail = close + self.atr_mult * atr
            return

        # Update trailing stop and apply exits
        if self.position.is_long:
            new_trail = close - self.atr_mult * atr
            self._trail = max(self._trail or new_trail, new_trail)
            if close <= float(self._trail) or bear:
                self.position.close()
                self._trail = None
        else:
            new_trail = close + self.atr_mult * atr
            self._trail = min(self._trail or new_trail, new_trail)
            if close >= float(self._trail) or bull:
                self.position.close()
                self._trail = None
