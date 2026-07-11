"""MA + Bollinger breakout. From set_1/003."""
from backtesting import Strategy
import numpy as np
import talib


class CatalogTrendFollowing(Strategy):
    fast = 20
    slow = 50
    bb_period = 20
    bb_nbdev = 2.0

    def init(self):
        self.fast_ma = self.I(talib.SMA, self.data.Close, timeperiod=self.fast)
        self.slow_ma = self.I(talib.SMA, self.data.Close, timeperiod=self.slow)
        u, m, l = self.I(
            talib.BBANDS,
            self.data.Close,
            timeperiod=self.bb_period,
            nbdevup=self.bb_nbdev,
            nbdevdn=self.bb_nbdev,
            matype=0,
        )
        self.bb_u, self.bb_m, self.bb_l = u, m, l

    def next(self):
        if len(self.data) < max(self.slow, self.bb_period) + 1:
            return
        c = self.data.Close[-1]
        if np.isnan(self.bb_u[-1]):
            return
        trend_up = self.fast_ma[-1] > self.slow_ma[-1]
        trend_dn = self.fast_ma[-1] < self.slow_ma[-1]
        if not self.position:
            if trend_up and c > self.bb_u[-1]:
                self.buy()
            elif trend_dn and c < self.bb_l[-1]:
                self.sell()
        else:
            if self.position.is_long and not trend_up:
                self.position.close()
            elif self.position.is_short and not trend_dn:
                self.position.close()
