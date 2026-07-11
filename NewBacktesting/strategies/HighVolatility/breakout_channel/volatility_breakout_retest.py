"""High-volatility breakout strategy that waits for a retest of the breakout level."""
import talib
from backtesting import Strategy


class VolatilityBreakoutRetest(Strategy):
    lookback = 20
    atr_period = 14
    atr_mult = 2.0

    def init(self):
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        self.high_max = self.I(talib.MAX, self.data.High, self.lookback)
        self.low_min = self.I(talib.MIN, self.data.Low, self.lookback)

    def next(self):
        if len(self.data) < self.lookback + 2:
            return

        if not self.position:
            if self.data.Close[-1] > self.high_max[-2] and self.data.Close[-2] <= self.high_max[-2]:
                entry = self.data.Close[-1]
                stop = entry - self.atr[-1] * self.atr_mult
                tp = entry + self.atr[-1] * self.atr_mult * 1.5
                self.buy(sl=stop, tp=tp)
            elif self.data.Close[-1] < self.low_min[-2] and self.data.Close[-2] >= self.low_min[-2]:
                entry = self.data.Close[-1]
                stop = entry + self.atr[-1] * self.atr_mult
                tp = entry - self.atr[-1] * self.atr_mult * 1.5
                self.sell(sl=stop, tp=tp)
