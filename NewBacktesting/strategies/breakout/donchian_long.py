"""
Donchian Channel Long Strategy - From 102/109.
Enter long when price breaks above 20-day high, exit when breaks below middle band.
"""
import numpy as np
import pandas as pd
from backtesting import Strategy


def _donchian_upper(high_series, period=20):
    return np.asarray(pd.Series(high_series).rolling(period).max())


def _donchian_lower(low_series, period=20):
    return np.asarray(pd.Series(low_series).rolling(period).min())


class DonchianLongStrategy(Strategy):
    """Donchian 20: long on breakout above upper, exit below middle (10-day low)."""

    lookback = 20

    def init(self):
        self.upper = self.I(lambda h: _donchian_upper(np.array(h), self.lookback), self.data.High)
        self.lower = self.I(lambda l: _donchian_lower(np.array(l), self.lookback), self.data.Low)
        mid = self.lookback // 2
        self.middle = self.I(lambda l: _donchian_lower(np.array(l), mid), self.data.Low)

    def next(self):
        if len(self.data) < self.lookback + 5:
            return
        if np.isnan(self.upper[-1]):
            return

        price = self.data.Close[-1]
        mid = self.middle[-1]
        upper_band = self.upper[-1]
        prev_upper = self.upper[-2] if len(self.data) >= 2 else upper_band

        breakout = price > prev_upper
        below_mid = price < mid

        if not self.position:
            if breakout:
                self.buy()
        else:
            if below_mid:
                self.position.close()
