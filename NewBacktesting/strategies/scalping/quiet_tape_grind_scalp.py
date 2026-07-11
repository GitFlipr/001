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


class QuietTapeGrindScalp(Strategy):
    """
    Low-volatility intraday: small targets when noise is muted and slow EMAs agree.
    """

    ema_fast = 10
    ema_slow = 50
    rsi_period = 5
    natr_period = 14
    natr_base = 80
    compress_below = 0.9
    atr_period = 14
    vol_window = 30
    risk_atr = 0.9
    reward_atr = 1.1

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume

        self.ema_f = self.I(talib.EMA, close, self.ema_fast)
        self.ema_s = self.I(talib.EMA, close, self.ema_slow)
        self.rsi = self.I(talib.RSI, close, self.rsi_period)
        self.atr = self.I(talib.ATR, high, low, close, self.atr_period)
        self.vol_sma = self.I(_rolling_mean, volume, self.vol_window)
        self.comp = self.I(_natr, high, low, close, self.natr_period, self.natr_base)

    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]
        if not np.isfinite(atr) or atr <= 0:
            return

        quiet = self.comp[-1] < self.compress_below
        vol_ok = self.data.Volume[-1] > 0.7 * self.vol_sma[-1]

        if not self.position:
            if quiet and vol_ok and self.ema_f[-1] > self.ema_s[-1] and 46 < self.rsi[-1] < 62:
                self.buy(sl=price - self.risk_atr * atr, tp=price + self.reward_atr * atr)
            elif quiet and vol_ok and self.ema_f[-1] < self.ema_s[-1] and 38 < self.rsi[-1] < 54:
                self.sell(sl=price + self.risk_atr * atr, tp=price - self.reward_atr * atr)
            return

        if self.position.is_long:
            if self.rsi[-1] > 66 or self.ema_f[-1] < self.ema_s[-1]:
                self.position.close()
        else:
            if self.rsi[-1] < 34 or self.ema_f[-1] > self.ema_s[-1]:
                self.position.close()
