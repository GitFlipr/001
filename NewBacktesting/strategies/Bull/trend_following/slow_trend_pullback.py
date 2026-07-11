"""
Multi-week / position-style bias: trade only in direction of long SMA; enter on pullback
to shorter mean. Strict conditions => fewer entries (aim: holds of many bars on daily TF).

Not financial advice.
"""
import numpy as np
import talib
from backtesting import Strategy


class SlowTrendPullbackStrategy(Strategy):
    """
    Uptrend: close > SMA(200). Long entry when RSI dips below rsi_buy AND still above SMA(200).
    Exit long: close under SMA(50) or RSI overbought rsi_sell.
    Mirrors "weekly bias, daily pullback" idea when run on daily OHLCV.
    """

    sma_trend = 200
    sma_exit = 50
    rsi_period = 14
    rsi_buy = 38
    rsi_sell = 72

    def init(self):
        c = self.data.Close
        self.sma200 = self.I(talib.SMA, c, timeperiod=self.sma_trend)
        self.sma50 = self.I(talib.SMA, c, timeperiod=self.sma_exit)
        self.rsi = self.I(talib.RSI, c, timeperiod=self.rsi_period)

    def next(self):
        if len(self.data) < self.sma_trend + 5 or np.isnan(self.rsi[-1]):
            return
        c = self.data.Close[-1]
        up = c > self.sma200[-1]
        down = c < self.sma200[-1]

        if not self.position:
            if up and self.rsi[-1] < self.rsi_buy and self.rsi[-1] > 25:
                self.buy()
            elif down and self.rsi[-1] > (100 - self.rsi_buy) and self.rsi[-1] < 75:
                self.sell()
        else:
            if self.position.is_long:
                if c < self.sma50[-1] or self.rsi[-1] > self.rsi_sell:
                    self.position.close()
            elif self.position.is_short:
                if c > self.sma50[-1] or self.rsi[-1] < (100 - self.rsi_sell):
                    self.position.close()
