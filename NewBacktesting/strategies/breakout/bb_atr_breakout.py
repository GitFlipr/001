"""Bollinger + ATR risk (breakout). From set_1/044."""
from backtesting import Strategy
import numpy as np
import talib


class BbAtrBreakout(Strategy):
    bb_period = 20
    bb_dev = 2.0
    atr_period = 14
    atr_sl = 1.375

    def init(self):
        u, m, l = self.I(
            talib.BBANDS,
            self.data.Close,
            timeperiod=self.bb_period,
            nbdevup=self.bb_dev,
            nbdevdn=self.bb_dev,
            matype=0,
        )
        self.bb_u, self.bb_m, self.bb_l = u, m, l
        self.atr = self.I(
            talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period
        )

    def next(self):
        if len(self.data) < max(self.bb_period, self.atr_period) + 2:
            return
        if np.isnan(self.atr[-1]):
            return
        c = self.data.Close[-1]
        if not self.position:
            if c > self.bb_u[-1]:
                self.buy()
            elif c < self.bb_l[-1]:
                self.sell()
        else:
            if self.position.is_long and c < self.bb_m[-1] - self.atr_sl * self.atr[-1]:
                self.position.close()
            elif self.position.is_short and c > self.bb_m[-1] + self.atr_sl * self.atr[-1]:
                self.position.close()
