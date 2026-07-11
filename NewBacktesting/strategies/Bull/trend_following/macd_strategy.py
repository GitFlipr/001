import numpy as np
import pandas as pd
from backtesting import Strategy
from backtesting.lib import crossover
import talib

class MACDStrategy(Strategy):
    fastperiod = 12
    slowperiod = 26
    signalperiod = 9
    atr_period = 14
    atr_multiplier = 2.0
    rr_ratio = 2.0

    def init(self):
        self.macd, self.signal, _ = self.I(talib.MACD, self.data.Close, self.fastperiod, self.slowperiod, self.signalperiod)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)

    def next(self):
        price = self.data.Close[-1]
        if np.isnan(self.macd[-1]) or np.isnan(self.signal[-1]) or np.isnan(self.atr[-1]):
            return
        if not self.position:
            if crossover(self.macd, self.signal):
                stop_loss = price - (self.atr[-1] * self.atr_multiplier)
                take_profit = price + (price - stop_loss) * self.rr_ratio
                self.buy(sl=stop_loss, tp=take_profit)
            elif crossover(self.signal, self.macd):
                stop_loss = price + (self.atr[-1] * self.atr_multiplier)
                take_profit = price - (stop_loss - price) * self.rr_ratio
                if take_profit < price < stop_loss:
                    self.sell(sl=stop_loss, tp=take_profit)
        elif self.position.is_long:
            if crossover(self.signal, self.macd):
                self.position.close()
        elif self.position.is_short:
            if crossover(self.macd, self.signal):
                self.position.close() 