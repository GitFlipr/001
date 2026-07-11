"""Basic Bollinger breakout with ATR stop (TA-Lib)."""

import numpy as np
import talib
from backtesting import Strategy


class BBandAtrBreakoutBasic(Strategy):
    bb_period = 20
    bb_dev = 2.0
    atr_period = 14
    atr_mult = 2.5

    trend_sma_period = 100

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low

        self.bb_up, self.bb_mid, self.bb_lo = self.I(
            talib.BBANDS, close, timeperiod=self.bb_period, nbdevup=self.bb_dev, nbdevdn=self.bb_dev
        )
        self.atr = self.I(talib.ATR, high, low, close, timeperiod=self.atr_period)
        self.trend = self.I(talib.SMA, close, timeperiod=self.trend_sma_period)

    def next(self):
        if len(self.data) < max(self.bb_period, self.atr_period, self.trend_sma_period) + 5:
            return

        c = float(self.data.Close[-1])
        atr = float(self.atr[-1])
        if np.isnan(atr) or atr <= 0:
            return

        bull = c >= float(self.trend[-1])
        bear = c <= float(self.trend[-1])

        up = float(self.bb_up[-1])
        lo = float(self.bb_lo[-1])
        if np.isnan(up) or np.isnan(lo):
            return

        if not self.position:
            if bull and c > up:
                sl = c - self.atr_mult * atr
                if sl < c:
                    self.buy(sl=sl)
            elif bear and c < lo:
                sl = c + self.atr_mult * atr
                if c < sl:
                    self.sell(sl=sl)
        else:
            # Simple mean reversion exit back to mid band.
            mid = float(self.bb_mid[-1])
            if np.isnan(mid):
                return
            if self.position.is_long and c < mid:
                self.position.close()
            elif self.position.is_short and c > mid:
                self.position.close()

