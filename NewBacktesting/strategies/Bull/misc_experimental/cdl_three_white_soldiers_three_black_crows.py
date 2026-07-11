"""
Three White Soldiers / Three Black Crows continuation.

Signals:
- Long on CDL3WHITESOLDIERS > 0
- Short on CDL3BLACKCROWS < 0 (some builds return negative)
- Exit on opposite signal
"""
from __future__ import annotations

import talib
from backtesting import Strategy


class CdlThreeSoldiersThreeCrows(Strategy):
    def init(self):
        self.soldiers = self.I(
            talib.CDL3WHITESOLDIERS,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )
        self.crows = self.I(
            talib.CDL3BLACKCROWS,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )

    def next(self):
        if len(self.data) < 10:
            return
        bull = float(self.soldiers[-1]) > 0
        bear = float(self.crows[-1]) < 0 or float(self.crows[-1]) > 0

        if not self.position:
            if bull:
                self.buy()
            elif bear:
                self.sell()
            return

        if self.position.is_long and bear:
            self.position.close()
        elif self.position.is_short and bull:
            self.position.close()
