"""Slow trend (momentum) with ATR stop sizing. Carry proxy. From set_1/023."""
from backtesting import Strategy
import numpy as np
import talib


class CarryTrendProxy(Strategy):
    sma_period = 100
    atr_period = 14

    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_period)
        self.atr = self.I(
            talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period
        )

    def next(self):
        if len(self.data) < self.sma_period + 2:
            return
        if np.isnan(self.atr[-1]):
            return
        c = self.data.Close[-1]
        if not self.position:
            if c > self.sma[-1]:
                self.buy()
            elif c < self.sma[-1]:
                self.sell()
        else:
            if self.position.is_long and c < self.sma[-1] - 0.5 * self.atr[-1]:
                self.position.close()
            elif self.position.is_short and c > self.sma[-1] + 0.5 * self.atr[-1]:
                self.position.close()
