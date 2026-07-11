from __future__ import annotations

import numpy as np
import pandas as pd
from backtesting import Strategy
import talib


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


def _rolling_max(arr, window):
    return pd.Series(arr).rolling(int(window)).max().to_numpy()


def _rolling_min(arr, window):
    return pd.Series(arr).rolling(int(window)).min().to_numpy()


class NeutralDonchianMidSwing(Strategy):
    """
    Neutral / range-biased swing: low ADX, trade mean reversion toward the midpoint of a Donchian channel.
    """

    dc_period = 55
    adx_period = 14
    adx_max = 22
    rsi_period = 14
    atr_period = 14
    vol_window = 30
    risk_atr = 2.0
    reward_atr = 2.8

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume

        self.adx = self.I(talib.ADX, high, low, close, self.adx_period)
        self.rsi = self.I(talib.RSI, close, self.rsi_period)
        self.atr = self.I(talib.ATR, high, low, close, self.atr_period)
        self.vol_sma = self.I(_rolling_mean, volume, self.vol_window)
        self.dc_hi = self.I(_rolling_max, high, self.dc_period)
        self.dc_lo = self.I(_rolling_min, low, self.dc_period)

    def next(self):
        atr = self.atr[-1]
        if not np.isfinite(atr) or atr <= 0:
            return

        neutral = self.adx[-1] < self.adx_max
        vol_ok = self.data.Volume[-1] >= self.vol_sma[-1]
        hi, lo = self.dc_hi[-1], self.dc_lo[-1]
        if not np.isfinite(hi) or not np.isfinite(lo) or hi <= lo:
            return
        mid = 0.5 * (hi + lo)
        price = self.data.Close[-1]

        if not self.position:
            if neutral and vol_ok and price <= lo + 0.15 * (hi - lo) and self.rsi[-1] < 42:
                self.buy(sl=price - self.risk_atr * atr, tp=price + self.reward_atr * atr)
            elif neutral and vol_ok and price >= hi - 0.15 * (hi - lo) and self.rsi[-1] > 58:
                self.sell(sl=price + self.risk_atr * atr, tp=price - self.reward_atr * atr)
            return

        if self.position.is_long:
            if price >= mid or self.adx[-1] > self.adx_max + 3:
                self.position.close()
        else:
            if price <= mid or self.adx[-1] > self.adx_max + 3:
                self.position.close()
