"""20/50 MA cross + RSI 50 filter. From set_2/081 (Strats08)."""
import numpy as np
import talib
from backtesting import Strategy
from backtesting.lib import crossover


class Strats08MaRsi(Strategy):
    fast = 20
    slow = 50
    rsi_period = 14

    def init(self):
        self.sma_f = self.I(talib.SMA, self.data.Close, timeperiod=self.fast)
        self.sma_s = self.I(talib.SMA, self.data.Close, timeperiod=self.slow)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)

    def next(self):
        if len(self.data) < self.slow + 2:
            return
        if np.isnan(self.rsi[-1]):
            return
        if not self.position:
            if crossover(self.sma_f, self.sma_s) and self.rsi[-1] > 50:
                self.buy()
            elif crossover(self.sma_s, self.sma_f) and self.rsi[-1] < 50:
                self.sell()
        else:
            if self.position.is_long and crossover(self.sma_s, self.sma_f):
                self.position.close()
            elif self.position.is_short and crossover(self.sma_f, self.sma_s):
                self.position.close()
