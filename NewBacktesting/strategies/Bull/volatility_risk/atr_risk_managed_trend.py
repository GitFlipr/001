"""SMA trend with ATR multiple stops. From set_2/070."""
import numpy as np
import talib
from backtesting import Strategy


class AtrRiskManagedTrend(Strategy):
    sma_period = 50
    atr_period = 14
    sl_mult = 2.0

    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_period)
        self.atr = self.I(
            talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period
        )

    def next(self):
        if len(self.data) < self.sma_period + 2:
            return
        if np.isnan(self.atr[-1]):
            return
        c = self.data.Close[-1]
        if not self.position:
            if c > self.sma[-1]:
                self.buy()
            elif c < self.sma[-1]:
                self.sell()
        else:
            if self.position.is_long and c < self.sma[-1] - self.sl_mult * self.atr[-1]:
                self.position.close()
            elif self.position.is_short and c > self.sma[-1] + self.sl_mult * self.atr[-1]:
                self.position.close()
