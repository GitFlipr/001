"""Momentum acceleration strategy that looks for strong directional continuation after a squeeze."""
import talib
from backtesting import Strategy


class TrendAccelerationReversal(Strategy):
    fast = 5
    slow = 20
    roc_period = 10

    def init(self):
        self.ema_fast = self.I(talib.EMA, self.data.Close, timeperiod=self.fast)
        self.ema_slow = self.I(talib.EMA, self.data.Close, timeperiod=self.slow)
        self.roc = self.I(talib.ROC, self.data.Close, timeperiod=self.roc_period)

    def next(self):
        if len(self.data) < self.slow + 2:
            return

        if not self.position:
            if self.ema_fast[-1] > self.ema_slow[-1] and self.roc[-1] > 0:
                self.buy()
            elif self.ema_fast[-1] < self.ema_slow[-1] and self.roc[-1] < 0:
                self.sell()
        else:
            if self.position.is_long and self.ema_fast[-1] < self.ema_slow[-1]:
                self.position.close()
            elif self.position.is_short and self.ema_fast[-1] > self.ema_slow[-1]:
                self.position.close()
