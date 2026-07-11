"""PL dot = SMA((H+L+C)/3); trade close vs dot. From set_2/064."""
import numpy as np
import talib
from backtesting import Strategy


def _pl_dot(high, low, close, period=10):
    tp = (high + low + close) / 3.0
    return talib.SMA(tp, timeperiod=period)


class PlDotStrategy(Strategy):
    period = 10

    def init(self):
        p = self.period
        self.pl = self.I(
            lambda h, l, c: _pl_dot(np.array(h), np.array(l), np.array(c), p),
            self.data.High, self.data.Low, self.data.Close,
        )

    def next(self):
        if len(self.data) < self.period + 2:
            return
        c = self.data.Close[-1]
        if np.isnan(self.pl[-1]):
            return
        if not self.position:
            if c > self.pl[-1]:
                self.buy()
            elif c < self.pl[-1]:
                self.sell()
        else:
            if self.position.is_long and c < self.pl[-1]:
                self.position.close()
            elif self.position.is_short and c > self.pl[-1]:
                self.position.close()
