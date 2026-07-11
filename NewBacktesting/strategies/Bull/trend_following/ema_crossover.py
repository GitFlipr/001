import talib
from backtesting import Strategy
from backtesting.lib import crossover


class EMACrossover(Strategy):
    n1 = 9
    n2 = 20

    def init(self):
        self.ema1 = self.I(talib.EMA, self.data.Close, timeperiod=self.n1)
        self.ema2 = self.I(talib.EMA, self.data.Close, timeperiod=self.n2)
    def next(self):
        if len(self.data) < 80:
            return
        if crossover(self.ema1, self.ema2):
            self.buy()
        elif crossover(self.ema2, self.ema1):
            self.sell()
