"""
Short holding / quick-turn style on whatever bar size you feed (e.g. 1h, 15m).
Tight RSI band + quick exit. High churn; costs matter.

Not financial advice.
"""
import numpy as np
import talib
from backtesting import Strategy


class RsiBurstScalpStrategy(Strategy):
    """
    Long: RSI(5) crosses up through oversold (was < lo, now > lo).
    Exit: RSI > hi_exit OR max_bars in trade.
    Symmetric for short.
    """

    rsi_period = 5
    rsi_lo = 22
    rsi_hi_exit = 58
    max_bars = 8

    def init(self):
        c = self.data.Close
        self.rsi = self.I(talib.RSI, c, timeperiod=self.rsi_period)
        self._entry_len = 0

    def next(self):
        if len(self.data) < self.rsi_period + 3 or np.isnan(self.rsi[-1]):
            return
        r, r_1 = self.rsi[-1], self.rsi[-2]

        if self.position:
            bars = len(self.data) - self._entry_len
            if self.position.is_long:
                if r > self.rsi_hi_exit or bars >= self.max_bars:
                    self.position.close()
            else:
                if r < (100 - self.rsi_hi_exit) or bars >= self.max_bars:
                    self.position.close()
            return

        if r_1 < self.rsi_lo <= r:
            self.buy()
            self._entry_len = len(self.data)
            return
        if r_1 > (100 - self.rsi_lo) >= r:
            self.sell()
            self._entry_len = len(self.data)
