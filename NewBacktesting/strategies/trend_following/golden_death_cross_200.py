"""50/200 SMA golden cross (long) and death cross (short). From set_1/007."""
from backtesting import Strategy
from backtesting.lib import crossover
import talib


class GoldenDeathCross200(Strategy):
    fast = 50
    slow = 200

    def init(self):
        self.sma_f = self.I(talib.SMA, self.data.Close, timeperiod=self.fast)
        self.sma_s = self.I(talib.SMA, self.data.Close, timeperiod=self.slow)

    def next(self):
        if len(self.data) < self.slow + 2:
            return
        if crossover(self.sma_f, self.sma_s):
            if self.position and self.position.is_short:
                self.position.close()
            self.buy()
        elif crossover(self.sma_s, self.sma_f):
            if self.position and self.position.is_long:
                self.position.close()
            self.sell()
