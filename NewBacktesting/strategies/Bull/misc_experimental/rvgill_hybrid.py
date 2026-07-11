"""RVGI proxy + SSL; cross confirmation. From set_2/071."""
import numpy as np
import talib
from backtesting import Strategy
from backtesting.lib import crossover


def _rvgi(high, low, open_, close, period=10):
    num = close - open_
    den = np.maximum(high - low, 1e-12)
    r = num / den
    return talib.SMA(r, timeperiod=period)


class RvgillHybrid(Strategy):
    ssl_period = 20
    rvgi_period = 10

    def init(self):
        self.ssl = self.I(talib.EMA, self.data.Close, timeperiod=self.ssl_period)
        rp = self.rvgi_period
        self.rvgi = self.I(
            lambda h, l, o, c: _rvgi(h, l, o, c, rp),
            self.data.High, self.data.Low, self.data.Open, self.data.Close,
        )
        self.rvgi_sig = self.I(talib.SMA, self.rvgi, timeperiod=4)

    def next(self):
        if len(self.data) < max(self.ssl_period, self.rvgi_period) + 5:
            return
        if np.isnan(self.rvgi[-1]):
            return
        c = self.data.Close[-1]
        if not self.position:
            if c > self.ssl[-1] and crossover(self.rvgi, self.rvgi_sig):
                self.buy()
            elif c < self.ssl[-1] and crossover(self.rvgi_sig, self.rvgi):
                self.sell()
        else:
            if self.position.is_long and c < self.ssl[-1]:
                self.position.close()
            elif self.position.is_short and c > self.ssl[-1]:
                self.position.close()
