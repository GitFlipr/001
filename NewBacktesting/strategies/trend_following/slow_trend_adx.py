"""50/200 SMA + ADX > 25 filter. From set_2/075."""
import numpy as np
import talib
from backtesting import Strategy
from backtesting.lib import crossover


class SlowTrendAdx(Strategy):
    fast = 50
    slow = 200
    adx_period = 14
    adx_min = 25

    def init(self):
        self.sma_f = self.I(talib.SMA, self.data.Close, timeperiod=self.fast)
        self.sma_s = self.I(talib.SMA, self.data.Close, timeperiod=self.slow)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_period)

    def next(self):
        if len(self.data) < self.slow + 2:
            return
        if np.isnan(self.adx[-1]) or self.adx[-1] < self.adx_min:
            return
        if not self.position:
            if crossover(self.sma_f, self.sma_s):
                self.buy()
            elif crossover(self.sma_s, self.sma_f):
                self.sell()
        else:
            if self.adx[-1] < 20:
                self.position.close()
