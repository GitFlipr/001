from __future__ import annotations

import numpy as np
import pandas as pd
from backtesting import Strategy
import talib


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


class RegimeEmaAdxSwing(Strategy):
    """
    Bear-regime swing strategy.
    Prefers short continuation entries with ADX confirmation and volatility-aware exits.
    """

    ema_fast = 21
    ema_slow = 89
    adx_period = 14
    adx_min = 20
    rsi_period = 14
    rsi_short_max = 52
    atr_period = 14
    vol_window = 30
    risk_atr = 2.2
    reward_atr = 3.4

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume

        self.ema_f = self.I(talib.EMA, close, self.ema_fast)
        self.ema_s = self.I(talib.EMA, close, self.ema_slow)
        self.adx = self.I(talib.ADX, high, low, close, self.adx_period)
        self.rsi = self.I(talib.RSI, close, self.rsi_period)
        self.atr = self.I(talib.ATR, high, low, close, self.atr_period)
        self.vol_sma = self.I(_rolling_mean, volume, self.vol_window)

    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]
        if not np.isfinite(atr) or atr <= 0:
            return

        bear_regime = self.ema_f[-1] < self.ema_s[-1]
        trend_ok = self.adx[-1] >= self.adx_min
        vol_ok = self.data.Volume[-1] >= self.vol_sma[-1]

        if not self.position:
            # Enter continuation short after weak bounce in established downtrend.
            if bear_regime and trend_ok and vol_ok and self.rsi[-1] < self.rsi_short_max and price < self.ema_f[-1]:
                self.sell(sl=price + self.risk_atr * atr, tp=price - self.reward_atr * atr)
            return

        # Exit when regime weakens or trend compression appears.
        if self.position.is_short:
            if self.ema_f[-1] > self.ema_s[-1] or self.adx[-1] < (self.adx_min - 4):
                self.position.close()
