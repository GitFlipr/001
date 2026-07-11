"""MACD momentum + middle Bollinger mean reversion exit. From set_2/096 (Strats22)."""
import numpy as np
import talib
from backtesting import Strategy
from backtesting.lib import crossover


class Strats22MacdBb(Strategy):
    bb_period = 20

    def init(self):
        self.macd, self.macds, _ = self.I(talib.MACD, self.data.Close)
        _, self.bb_m, _ = self.I(
            talib.BBANDS,
            self.data.Close,
            timeperiod=self.bb_period,
            nbdevup=2.0,
            nbdevdn=2.0,
            matype=0,
        )

    def next(self):
        if len(self.data) < self.bb_period + 3:
            return
        if np.isnan(self.macd[-1]):
            return
        if not self.position:
            if crossover(self.macd, self.macds):
                self.buy()
            elif crossover(self.macds, self.macd):
                self.sell()
        else:
            c = self.data.Close[-1]
            if self.position.is_long and (crossover(self.macds, self.macd) or c < self.bb_m[-1]):
                self.position.close()
            elif self.position.is_short and (crossover(self.macd, self.macds) or c > self.bb_m[-1]):
                self.position.close()
