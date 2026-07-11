"""
The 5% Trading Strategy (1-minute Scalp) - From 104.
50 EMA x 100 EMA, pullback to EMA, Stochastic 3,2,2.
"""
import numpy as np
from backtesting import Strategy
from backtesting.lib import crossover
import talib


class FivePercentScalpStrategy(Strategy):
    """
    Long: 50 EMA > 100 EMA, price pullback near EMA, Stoch > 20.
    Short: 50 EMA < 100 EMA, price pullback near EMA, Stoch < 80.
    """
    ema_fast = 50
    ema_slow = 100
    stoch_k = 3
    stoch_d = 2
    stoch_smooth = 2
    pullback_pct = 0.005

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        self.ema50 = self.I(talib.EMA, close, timeperiod=self.ema_fast)
        self.ema100 = self.I(talib.EMA, close, timeperiod=self.ema_slow)
        self.stoch_k, self.stoch_d = self.I(
            talib.STOCH, high, low, close,
            fastk_period=self.stoch_k, slowk_period=self.stoch_smooth, slowk_matype=0,
            slowd_period=self.stoch_d, slowd_matype=0
        )

    def next(self):
        if len(self.data) < self.ema_slow + 5:
            return
        if np.isnan(self.ema100[-1]) or np.isnan(self.stoch_k[-1]):
            return

        price = self.data.Close[-1]
        near_ema50 = abs(price - self.ema50[-1]) / (self.ema50[-1] + 1e-10) < self.pullback_pct
        near_ema100 = abs(price - self.ema100[-1]) / (self.ema100[-1] + 1e-10) < self.pullback_pct
        near_ema = near_ema50 or near_ema100

        bullish_trend = self.ema50[-1] > self.ema100[-1]
        bearish_trend = self.ema50[-1] < self.ema100[-1]
        stoch_up = self.stoch_k[-1] > 20
        stoch_down = self.stoch_k[-1] < 80

        if not self.position:
            if bullish_trend and near_ema and stoch_up:
                self.buy()
            elif bearish_trend and near_ema and stoch_down:
                self.sell()
        else:
            if self.position.is_long and crossover(self.ema100, self.ema50):
                self.position.close()
            elif self.position.is_short and crossover(self.ema50, self.ema100):
                self.position.close()
