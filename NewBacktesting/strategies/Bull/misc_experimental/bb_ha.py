"""Bollinger breakout (21, 2.7) + Heikin-Ashi EMA proxy for trend. From set_2/092 (Strats18)."""
import numpy as np
import talib
from backtesting import Strategy


def _smooth_tp(open_, high, low, close):
    tp = (open_ + high + low + close) / 4.0
    return talib.EMA(tp, timeperiod=5)


class Strats18BbHa(Strategy):
    bb_period = 21
    bb_dev = 2.7

    def init(self):
        self.bb_u, _, self.bb_l = self.I(
            talib.BBANDS,
            self.data.Close,
            timeperiod=self.bb_period,
            nbdevup=self.bb_dev,
            nbdevdn=self.bb_dev,
            matype=0,
        )
        self.sm = self.I(
            _smooth_tp,
            self.data.Open, self.data.High, self.data.Low, self.data.Close,
        )

    def next(self):
        if len(self.data) < self.bb_period + 5:
            return
        if np.isnan(self.bb_u[-1]):
            return
        c = self.data.Close[-1]
        ha_bull = self.sm[-1] > self.sm[-2]
        if not self.position:
            if c > self.bb_u[-1] and ha_bull:
                self.buy()
            elif c < self.bb_l[-1] and not ha_bull:
                self.sell()
        else:
            if self.position.is_long and not ha_bull:
                self.position.close()
            elif self.position.is_short and ha_bull:
                self.position.close()
