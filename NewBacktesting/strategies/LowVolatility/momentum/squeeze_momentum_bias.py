"""Low-volatility momentum bias built around a simple squeeze-style filter."""
import talib
from backtesting import Strategy


class SqueezeMomentumBias(Strategy):
    fast = 8
    slow = 21
    bb_period = 20
    bb_std = 2.0

    def init(self):
        self.ema_fast = self.I(talib.EMA, self.data.Close, timeperiod=self.fast)
        self.ema_slow = self.I(talib.EMA, self.data.Close, timeperiod=self.slow)
        self.upper, self.middle, self.lower = self.I(talib.BBANDS, self.data.Close, self.bb_period, self.bb_std, self.bb_std)

    def next(self):
        if len(self.data) < self.slow + 2:
            return

        if not self.position:
            if self.ema_fast[-1] > self.ema_slow[-1] and self.data.Close[-1] > self.middle[-1]:
                self.buy()
            elif self.ema_fast[-1] < self.ema_slow[-1] and self.data.Close[-1] < self.middle[-1]:
                self.sell()
        else:
            if self.position.is_long and (self.ema_fast[-1] < self.ema_slow[-1] or self.data.Close[-1] < self.lower[-1]):
                self.position.close()
            elif self.position.is_short and (self.ema_fast[-1] > self.ema_slow[-1] or self.data.Close[-1] > self.upper[-1]):
                self.position.close()
