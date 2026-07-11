"""Triple EMA (50/100/200) + MACD confirmation. From set_2/090,091 (Strats16,17)."""
import numpy as np
import talib
from backtesting import Strategy
from backtesting.lib import crossover


class Strats16TripleEmaMacd(Strategy):
    e1, e2, e3 = 50, 100, 200

    def init(self):
        self.ema1 = self.I(talib.EMA, self.data.Close, timeperiod=self.e1)
        self.ema2 = self.I(talib.EMA, self.data.Close, timeperiod=self.e2)
        self.ema3 = self.I(talib.EMA, self.data.Close, timeperiod=self.e3)
        self.macd, self.macds, _ = self.I(talib.MACD, self.data.Close)

    def next(self):
        if len(self.data) < self.e3 + 3:
            return
        if np.isnan(self.macd[-1]):
            return
        bull = self.ema1[-1] > self.ema2[-1] > self.ema3[-1]
        bear = self.ema1[-1] < self.ema2[-1] < self.ema3[-1]
        if not self.position:
            if bull and crossover(self.macd, self.macds):
                self.buy()
            elif bear and crossover(self.macds, self.macd):
                self.sell()
        else:
            if self.position.is_long and (not bull or crossover(self.macds, self.macd)):
                self.position.close()
            elif self.position.is_short and (not bear or crossover(self.macd, self.macds)):
                self.position.close()


class Strats17TripleEmaMacd(Strats16TripleEmaMacd):
    """Same as Strats16; alias for compatibility."""
