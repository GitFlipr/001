"""
BTC-oriented template: slower MAs + stricter ADX (large-cap, often mean-reverting intraday;
on daily/4h many traders use 50/200 context). Tune on BTCUSDT/BTC-PERP history only.

Not financial advice.
"""
import numpy as np
import talib
from backtesting import Strategy


class BtcRegimeTrendStrategy(Strategy):
    """
    Long: price > SMA(200), SMA(50) > SMA(200), ADX > 20.
    Exit long: close < SMA(50) or SMA(50) < SMA(200).
    Designed as a single-market module you run on BTC OHLCV.
    """

    sma_fast = 50
    sma_slow = 200
    adx_period = 14
    adx_min = 20

    def init(self):
        c = self.data.Close
        h, l = self.data.High, self.data.Low
        self.s50 = self.I(talib.SMA, c, timeperiod=self.sma_fast)
        self.s200 = self.I(talib.SMA, c, timeperiod=self.sma_slow)
        self.adx = self.I(talib.ADX, h, l, c, timeperiod=self.adx_period)

    def next(self):
        if len(self.data) < self.sma_slow + 5 or np.isnan(self.adx[-1]):
            return
        c = self.data.Close[-1]
        bull = c > self.s200[-1] and self.s50[-1] > self.s200[-1] and self.adx[-1] >= self.adx_min
        bear = c < self.s200[-1] and self.s50[-1] < self.s200[-1] and self.adx[-1] >= self.adx_min

        if not self.position:
            if bull:
                self.buy()
            elif bear:
                self.sell()
        else:
            if self.position.is_long and (c < self.s50[-1] or self.s50[-1] < self.s200[-1]):
                self.position.close()
            elif self.position.is_short and (c > self.s50[-1] or self.s50[-1] > self.s200[-1]):
                self.position.close()
