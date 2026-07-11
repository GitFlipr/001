"""
Aggressive bull-trend template: stacked rising EMAs + MACD histogram momentum.
Only chases strong trends; can give back fast in chop — use with regime filter in live.

Not financial advice.
"""
import numpy as np
import talib
from backtesting import Strategy
from backtesting.lib import crossover


class StackedEmaParabolicStrategy(Strategy):
    """
    Long: EMA8 > EMA21 > EMA55 and MACD line > signal and hist increasing.
    Exit long: EMA8 crosses below EMA21 or MACD bear cross.
    Short mirror for deep bear legs (optional; often disabled in pure bull tools).
    """

    e1, e2, e3 = 8, 21, 55

    def init(self):
        c = self.data.Close
        self.ema1 = self.I(talib.EMA, c, timeperiod=self.e1)
        self.ema2 = self.I(talib.EMA, c, timeperiod=self.e2)
        self.ema3 = self.I(talib.EMA, c, timeperiod=self.e3)
        self.macd, self.signal, self.hist = self.I(talib.MACD, c)

    def next(self):
        if len(self.data) < self.e3 + 5 or np.isnan(self.hist[-1]):
            return
        stack_bull = self.ema1[-1] > self.ema2[-1] > self.ema3[-1]
        stack_bear = self.ema1[-1] < self.ema2[-1] < self.ema3[-1]
        hist_rise = self.hist[-1] > self.hist[-2]
        hist_fall = self.hist[-1] < self.hist[-2]

        if not self.position:
            if stack_bull and self.macd[-1] > self.signal[-1] and hist_rise:
                self.buy()
            elif stack_bear and self.macd[-1] < self.signal[-1] and hist_fall:
                self.sell()
        else:
            if self.position.is_long:
                if crossover(self.ema2, self.ema1) or crossover(self.signal, self.macd):
                    self.position.close()
            elif self.position.is_short:
                if crossover(self.ema1, self.ema2) or crossover(self.macd, self.signal):
                    self.position.close()
