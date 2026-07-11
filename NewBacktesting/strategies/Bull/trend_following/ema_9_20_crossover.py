"""9 EMA vs 20 EMA crossover. From set_1/008."""
import talib
from backtesting import Strategy
from backtesting.lib import crossover


class EMA920Crossover(Strategy):
    n1 = 9
    n2 = 20

    def init(self):
        self.e1 = self.I(talib.EMA, self.data.Close, timeperiod=self.n1)
        self.e2 = self.I(talib.EMA, self.data.Close, timeperiod=self.n2)

    def next(self):
        if len(self.data) < self.n2 + 2:
            return
        if crossover(self.e1, self.e2):
            if self.position and self.position.is_short:
                self.position.close()
            self.buy()
        elif crossover(self.e2, self.e1):
            if self.position and self.position.is_long:
                self.position.close()
            self.sell()
