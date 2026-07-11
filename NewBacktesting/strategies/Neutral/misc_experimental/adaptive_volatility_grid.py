"""Experimental volatility-aware grid strategy for sideways or choppy markets."""
import talib
from backtesting import Strategy


class AdaptiveVolatilityGrid(Strategy):
    fast = 8
    slow = 21
    atr_period = 14
    grid_mult = 1.0

    def init(self):
        self.fast_ema = self.I(talib.EMA, self.data.Close, timeperiod=self.fast)
        self.slow_ema = self.I(talib.EMA, self.data.Close, timeperiod=self.slow)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)

    def next(self):
        if len(self.data) < self.slow + 2:
            return

        if not self.position:
            if self.fast_ema[-1] > self.slow_ema[-1] and self.atr[-1] < self.atr[-2]:
                self.buy()
            elif self.fast_ema[-1] < self.slow_ema[-1] and self.atr[-1] < self.atr[-2]:
                self.sell()
        else:
            if self.position.is_long and self.fast_ema[-1] < self.slow_ema[-1]:
                self.position.close()
            elif self.position.is_short and self.fast_ema[-1] > self.slow_ema[-1]:
                self.position.close()
