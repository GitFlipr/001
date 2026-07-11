"""12-cycle strategy inspired by recurring life cycles and “blessings within numbers”.

This is *not* a religious claim or prediction; it’s a numeric, repeatable rule-set that uses
the prominence of 12 as a design constraint:
- 12-period trend (SMA12)
- 12-period momentum (ROC12)
- 12-bar “commitment” hold window (avoid over-trading)
"""

import numpy as np
import talib
from backtesting import Strategy


class TwelveCycleMomentum(Strategy):
    sma_period = 12
    roc_period = 12
    hold_bars = 12

    roc_min = 0.3  # percent

    def init(self):
        c = self.data.Close
        self.sma = self.I(talib.SMA, c, timeperiod=self.sma_period)
        self.roc = self.I(talib.ROC, c, timeperiod=self.roc_period)
        self._bars_in_trade = 0

    def next(self):
        need = max(self.sma_period, self.roc_period) + 5
        if len(self.data) < need:
            return

        c = float(self.data.Close[-1])
        sma = float(self.sma[-1])
        roc = float(self.roc[-1])
        if any(np.isnan(x) for x in (sma, roc)):
            return

        if self.position:
            self._bars_in_trade += 1
            # Exit if trend breaks or the “12-bar cycle” completes.
            if self._bars_in_trade >= self.hold_bars:
                self.position.close()
                return
            if self.position.is_long and c < sma:
                self.position.close()
            elif self.position.is_short and c > sma:
                self.position.close()
            return

        # Flat: start a new “cycle” only when both trend + momentum agree.
        self._bars_in_trade = 0
        if c > sma and roc >= self.roc_min:
            self.buy()
        elif c < sma and roc <= -self.roc_min:
            self.sell()

