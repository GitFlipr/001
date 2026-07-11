"""Basic MACD histogram trend strategy (TA-Lib)."""

import numpy as np
import talib
from backtesting import Strategy


class MacdHistogramTrendBasic(Strategy):
    fast = 12
    slow = 26
    signal = 9
    ema_trend = 200

    def init(self):
        close = self.data.Close
        self.macd, self.macd_sig, self.macd_hist = self.I(
            talib.MACD, close, fastperiod=self.fast, slowperiod=self.slow, signalperiod=self.signal
        )
        self.trend = self.I(talib.EMA, close, timeperiod=self.ema_trend)

    def next(self):
        if len(self.data) < max(self.slow, self.signal, self.ema_trend) + 5:
            return

        c = float(self.data.Close[-1])
        t = float(self.trend[-1])
        h = float(self.macd_hist[-1])
        hs = float(self.macd_hist[-2])
        if any(np.isnan(x) for x in (t, h, hs)):
            return

        bull = c > t
        bear = c < t
        hist_up = h > 0 and h > hs
        hist_dn = h < 0 and h < hs

        if not self.position:
            if bull and hist_up:
                self.buy()
            elif bear and hist_dn:
                self.sell()
        else:
            if self.position.is_long and h < 0:
                self.position.close()
            elif self.position.is_short and h > 0:
                self.position.close()

