"""
Conservative trend: higher timeframe bias + ADX + slow MA.
Designed for fewer trades, defined trend filter (aim: smoother equity, lower churn).

Not financial advice. Backtest on your data and costs.
"""
import numpy as np
import talib
from backtesting import Strategy


class DualFilterTrendStrategy(Strategy):
    """
    Long only when: Close > SMA(slow), SMA(fast) > SMA(slow), ADX > threshold.
    Exit: close below slow SMA or ADX collapses below exit_adx.
    Short symmetric. Targets "reliable" trend participation, not scalps.
    """

    fast = 30
    slow = 100
    adx_period = 14
    adx_entry = 22
    adx_exit = 18

    def init(self):
        c = self.data.Close
        h, l = self.data.High, self.data.Low
        self.sma_f = self.I(talib.SMA, c, timeperiod=self.fast)
        self.sma_s = self.I(talib.SMA, c, timeperiod=self.slow)
        self.adx = self.I(talib.ADX, h, l, c, timeperiod=self.adx_period)

    def next(self):
        if len(self.data) < self.slow + 5 or np.isnan(self.adx[-1]):
            return
        c = self.data.Close[-1]
        trend_ok = self.sma_f[-1] > self.sma_s[-1]
        trend_down = self.sma_f[-1] < self.sma_s[-1]
        strong = self.adx[-1] >= self.adx_entry

        if not self.position:
            if trend_ok and strong and c > self.sma_s[-1]:
                self.buy()
            elif trend_down and strong and c < self.sma_s[-1]:
                self.sell()
        else:
            if self.position.is_long:
                if c < self.sma_s[-1] or self.adx[-1] < self.adx_exit:
                    self.position.close()
            elif self.position.is_short:
                if c > self.sma_s[-1] or self.adx[-1] < self.adx_exit:
                    self.position.close()
