from __future__ import annotations

import numpy as np
import pandas as pd
from backtesting import Strategy
import talib


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


def _natr(high, low, close, period, baseline_period):
    n = pd.Series(talib.NATR(high, low, close, timeperiod=int(period)), dtype=float)
    base = n.rolling(int(baseline_period)).mean().replace(0, np.nan)
    return (n / base).fillna(1.0).to_numpy()


class CompressionBreakoutSwing(Strategy):
    """
    Low-volatility swing: wait for volatility compression vs baseline, then trade breakouts.
    """

    ema_fast = 20
    ema_slow = 100
    adx_period = 14
    natr_period = 14
    natr_base = 100
    compress_below = 0.85
    rsi_period = 14
    atr_period = 14
    vol_window = 30
    breakout_ema_dist = 0.15
    risk_atr = 1.8
    reward_atr = 3.2

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
        self.comp = self.I(_natr, high, low, close, self.natr_period, self.natr_base)

    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]
        if not np.isfinite(atr) or atr <= 0:
            return

        calm = self.comp[-1] < self.compress_below
        vol_ok = self.data.Volume[-1] >= self.vol_sma[-1]
        up_bias = self.ema_f[-1] > self.ema_s[-1]
        dn_bias = self.ema_f[-1] < self.ema_s[-1]

        if not self.position:
            if calm and vol_ok and up_bias and price > self.ema_f[-1] + self.breakout_ema_dist * atr and self.rsi[-1] > 52:
                self.buy(sl=price - self.risk_atr * atr, tp=price + self.reward_atr * atr)
            elif calm and vol_ok and dn_bias and price < self.ema_f[-1] - self.breakout_ema_dist * atr and self.rsi[-1] < 48:
                self.sell(sl=price + self.risk_atr * atr, tp=price - self.reward_atr * atr)
            return

        if self.position.is_long:
            if self.comp[-1] > 1.05 or self.ema_f[-1] < self.ema_s[-1]:
                self.position.close()
        else:
            if self.comp[-1] > 1.05 or self.ema_f[-1] > self.ema_s[-1]:
                self.position.close()
