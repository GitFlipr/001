"""RSI vs price rolling extrema divergence proxy. From set_2/099 (Strats25)."""
import numpy as np
import talib
from backtesting import Strategy


class Strats25RsiDivergence(Strategy):
    rsi_period = 14
    lookback = 7

    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.ph = self.I(talib.MAX, self.data.High, timeperiod=self.lookback)
        self.pl = self.I(talib.MIN, self.data.Low, timeperiod=self.lookback)

    def next(self):
        if len(self.data) < self.rsi_period + self.lookback + 2:
            return
        if np.isnan(self.rsi[-1]):
            return
        if not self.position:
            if self.data.High[-1] >= self.ph[-2] and self.rsi[-1] < self.rsi[-4]:
                self.sell()
            elif self.data.Low[-1] <= self.pl[-2] and self.rsi[-1] > self.rsi[-4]:
                self.buy()
        else:
            if self.position.is_short and self.rsi[-1] < 30:
                self.position.close()
            elif self.position.is_long and self.rsi[-1] > 70:
                self.position.close()
