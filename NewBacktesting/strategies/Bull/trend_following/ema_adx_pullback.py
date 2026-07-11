"""Bull-market pullback strategy with EMA trend confirmation and ATR-based exits."""
import talib
from backtesting import Strategy


class EMAPullbackTrend(Strategy):
    fast = 8
    slow = 21
    atr_period = 14
    risk_mult = 1.5

    def init(self):
        self.fast_ema = self.I(talib.EMA, self.data.Close, timeperiod=self.fast)
        self.slow_ema = self.I(talib.EMA, self.data.Close, timeperiod=self.slow)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_period)

    def next(self):
        if len(self.data) < self.slow + 2:
            return

        if not self.position:
            if (
                self.fast_ema[-1] > self.slow_ema[-1]
                and self.data.Close[-2] <= self.fast_ema[-2]
                and self.data.Close[-1] > self.fast_ema[-1]
            ):
                entry = self.data.Close[-1]
                stop = entry - self.atr[-1] * self.risk_mult
                tp = entry + self.atr[-1] * self.risk_mult * 2
                self.buy(sl=stop, tp=tp)

        else:
            if self.position.is_long:
                if self.fast_ema[-1] < self.slow_ema[-1] or self.data.Close[-1] < self.fast_ema[-1]:
                    self.position.close()
            else:
                if self.fast_ema[-1] > self.slow_ema[-1] or self.data.Close[-1] > self.fast_ema[-1]:
                    self.position.close()
