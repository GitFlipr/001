"""Donchian breakout in direction of 200 SMA. From set_2/076."""
import talib
from backtesting import Strategy


class SlowTurtle(Strategy):
    n = 55
    trend_ma = 200

    def init(self):
        self.upper = self.I(talib.MAX, self.data.High, timeperiod=self.n)
        self.lower = self.I(talib.MIN, self.data.Low, timeperiod=self.n)
        self.sma200 = self.I(talib.SMA, self.data.Close, timeperiod=self.trend_ma)

    def next(self):
        if len(self.data) < max(self.n, self.trend_ma) + 2:
            return
        c = self.data.Close[-1]
        up = self.data.Close[-1] > self.upper[-2]
        dn = self.data.Close[-1] < self.lower[-2]
        if not self.position:
            if c > self.sma200[-1] and up:
                self.buy()
            elif c < self.sma200[-1] and dn:
                self.sell()
        else:
            if self.position.is_long and c < self.sma200[-1]:
                self.position.close()
            elif self.position.is_short and c > self.sma200[-1]:
                self.position.close()
