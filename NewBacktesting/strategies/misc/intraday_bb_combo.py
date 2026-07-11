"""Intraday BB: breakout + mean reversion toward middle. From set_1/050."""
from backtesting import Strategy
import numpy as np
import talib


def _bb_width(close, period=20, dev=2.0):
    u, m, l = talib.BBANDS(close, timeperiod=period, nbdevup=dev, nbdevdn=dev, matype=0)
    mid = np.where(m == 0, np.nan, m)
    return (u - l) / mid


class IntradayBbCombo(Strategy):
    period = 20
    dev = 2.0

    def init(self):
        u, m, l = self.I(
            talib.BBANDS,
            self.data.Close,
            timeperiod=self.period,
            nbdevup=self.dev,
            nbdevdn=self.dev,
            matype=0,
        )
        self.bb_u, self.bb_m, self.bb_l = u, m, l
        self.bw = self.I(lambda c: _bb_width(np.array(c), self.period, self.dev), self.data.Close)

    def next(self):
        if len(self.data) < self.period + 25:
            return
        c = self.data.Close[-1]
        m = self.bb_m[-1]
        if np.isnan(self.bb_u[-1]) or np.isnan(self.bw[-1]):
            return
        bw_hist = self.bw[-22:-2]
        narrow = self.bw[-2] < np.nanmean(bw_hist)

        if not self.position:
            if narrow and c > self.bb_u[-1]:
                self.buy()
            elif narrow and c < self.bb_l[-1]:
                self.sell()
        else:
            if self.position.is_long and c <= m:
                self.position.close()
            elif self.position.is_short and c >= m:
                self.position.close()
