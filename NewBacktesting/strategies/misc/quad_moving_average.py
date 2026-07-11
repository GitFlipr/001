"""5/10/20/50 SMA stacked alignment. From set_2/061."""
import numpy as np
import talib
from backtesting import Strategy


class QuadMovingAverage(Strategy):
    p1, p2, p3, p4 = 5, 10, 20, 50

    def init(self):
        self.ma1 = self.I(talib.SMA, self.data.Close, timeperiod=self.p1)
        self.ma2 = self.I(talib.SMA, self.data.Close, timeperiod=self.p2)
        self.ma3 = self.I(talib.SMA, self.data.Close, timeperiod=self.p3)
        self.ma4 = self.I(talib.SMA, self.data.Close, timeperiod=self.p4)

    def next(self):
        if len(self.data) < self.p4 + 2:
            return
        a, b, c, d = self.ma1[-1], self.ma2[-1], self.ma3[-1], self.ma4[-1]
        if np.isnan(d):
            return
        bull = a > b > c > d
        bear = a < b < c < d
        if not self.position:
            if bull:
                self.buy()
            elif bear:
                self.sell()
        else:
            if self.position.is_long and not bull:
                self.position.close()
            elif self.position.is_short and not bear:
                self.position.close()
