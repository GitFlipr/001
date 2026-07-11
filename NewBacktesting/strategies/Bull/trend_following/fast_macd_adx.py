"""Fast MACD (6,13,5) with ADX filter. From set_1/038."""
from backtesting import Strategy
from backtesting.lib import crossover
import numpy as np
import talib


class FastMacdAdx(Strategy):
    adx_period = 14
    adx_min = 25

    def init(self):
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_period)
        self.macd, self.macds, _ = self.I(talib.MACD, self.data.Close, 6, 13, 5)

    def next(self):
        if len(self.data) < 30:
            return
        if np.isnan(self.adx[-1]) or np.isnan(self.macd[-1]):
            return
        if self.adx[-1] < self.adx_min:
            return
        if not self.position:
            if crossover(self.macd, self.macds):
                self.buy()
            elif crossover(self.macds, self.macd):
                self.sell()
        else:
            if self.position.is_long and crossover(self.macds, self.macd):
                self.position.close()
            elif self.position.is_short and crossover(self.macd, self.macds):
                self.position.close()
