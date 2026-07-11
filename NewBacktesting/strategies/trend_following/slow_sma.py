"""Slow SMA trend following. From set_2/089 (Strats15)."""
import talib
from backtesting import Strategy


class Strats15SlowSma(Strategy):
    period = 100

    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.period)

    def next(self):
        if len(self.data) < self.period + 2:
            return
        c = self.data.Close[-1]
        if not self.position:
            if c > self.sma[-1]:
                self.buy()
            elif c < self.sma[-1]:
                self.sell()
        else:
            if self.position.is_long and c < self.sma[-1]:
                self.position.close()
            elif self.position.is_short and c > self.sma[-1]:
                self.position.close()
