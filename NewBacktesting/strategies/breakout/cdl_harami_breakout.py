"""
Harami (bull/bear) + breakout confirmation.

Harami alone can be noisy, so this adds a 1-bar breakout confirmation:
- Bull harami then next bar Close > prior High => long
- Bear harami then next bar Close < prior Low => short

Exit on opposite confirmed signal.
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy


class CdlHaramiBreakout(Strategy):
    lookahead_confirm = 1  # fixed for backtesting.py (uses next bar logic)

    def init(self):
        self.harami = self.I(
            talib.CDLHARAMI,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )

    def next(self):
        i = len(self.data) - 1
        if i < 3:
            return
        # Confirm harami occurred on previous bar
        har_prev = float(self.harami[-2])
        bull_setup = har_prev > 0
        bear_setup = har_prev < 0

        prev_high = float(self.data.High[-2])
        prev_low = float(self.data.Low[-2])
        close = float(self.data.Close[-1])

        bull = bull_setup and close > prev_high
        bear = bear_setup and close < prev_low

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
