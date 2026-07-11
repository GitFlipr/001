"""20/50 SMA cross + RSI above/below 50. From set_2/060."""
import numpy as np
import talib
from backtesting import Strategy
from backtesting.lib import crossover


class MultipleTrendFollowing(Strategy):
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
            if self.position.is_long and (crossover(self.sma_s, self.sma_f) or self.rsi[-1] < 30):
                self.position.close()
            elif self.position.is_short and (crossover(self.sma_f, self.sma_s) or self.rsi[-1] > 70):
                self.position.close()
