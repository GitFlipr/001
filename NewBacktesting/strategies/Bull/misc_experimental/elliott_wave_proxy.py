"""MACD + swing trend (Elliott Wave proxy). From set_1/035."""
from backtesting import Strategy
from backtesting.lib import crossover
import numpy as np
import talib


class ElliottWaveProxy(Strategy):
    ema_period = 34

    def init(self):
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        self.macd, self.macds, _ = self.I(talib.MACD, self.data.Close)

    def next(self):
        if len(self.data) < self.ema_period + 2:
            return
        if np.isnan(self.macd[-1]):
            return
        if not self.position:
            if self.data.Close[-1] > self.ema[-1] and crossover(self.macd, self.macds):
                self.buy()
            elif self.data.Close[-1] < self.ema[-1] and crossover(self.macds, self.macd):
                self.sell()
        else:
            if self.position.is_long and crossover(self.macds, self.macd):
                self.position.close()
            elif self.position.is_short and crossover(self.macd, self.macds):
                self.position.close()
