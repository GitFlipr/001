from __future__ import annotations

import numpy as np
import pandas as pd
from backtesting import Strategy
import talib


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


def _atr_ratio(close, high, low, atr_period, baseline):
    atr = pd.Series(talib.ATR(high, low, close, timeperiod=int(atr_period)), dtype=float)
    baseline_atr = atr.rolling(int(baseline)).mean()
    r = atr / baseline_atr.replace(0, np.nan)
    return r.fillna(1.0).to_numpy()


class AtrExpansionTrendSwing(Strategy):
    """
    High-volatility swing: engage trend legs when ATR expands vs its longer baseline.
    """

    ema_fast = 13
    ema_slow = 55
    adx_period = 14
    adx_min = 18
    atr_period = 14
    atr_baseline = 80
    vol_mult = 1.25
    rsi_period = 14
    vol_window = 30
    risk_atr = 2.5
    reward_atr = 4.0

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
        self.atr_hot = self.I(_atr_ratio, close, high, low, self.atr_period, self.atr_baseline)

    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]
        if not np.isfinite(atr) or atr <= 0:
            return

        hot = self.atr_hot[-1] >= self.vol_mult
        vol_ok = self.data.Volume[-1] >= self.vol_sma[-1]
        trend_up = self.ema_f[-1] > self.ema_s[-1]
        trend_dn = self.ema_f[-1] < self.ema_s[-1]
        trend_ok = self.adx[-1] >= self.adx_min

        if not self.position:
            if hot and trend_ok and vol_ok and trend_up and 45 < self.rsi[-1] < 68:
                self.buy(sl=price - self.risk_atr * atr, tp=price + self.reward_atr * atr)
            elif hot and trend_ok and vol_ok and trend_dn and 32 < self.rsi[-1] < 55:
                self.sell(sl=price + self.risk_atr * atr, tp=price - self.reward_atr * atr)
            return

        if self.position.is_long:
            if self.atr_hot[-1] < 1.0 or self.ema_f[-1] < self.ema_s[-1]:
                self.position.close()
        else:
            if self.atr_hot[-1] < 1.0 or self.ema_f[-1] > self.ema_s[-1]:
                self.position.close()
