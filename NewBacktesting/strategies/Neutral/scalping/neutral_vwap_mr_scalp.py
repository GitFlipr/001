from __future__ import annotations

import numpy as np
import pandas as pd
from backtesting import Strategy
import talib


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


def _vwap_approx(h, l, c, v):
    """Session-agnostic VWAP proxy: cumulative typical price * volume / cumulative volume."""
    tp = (pd.Series(h) + pd.Series(l) + pd.Series(c)) / 3.0
    vol = pd.Series(v).astype(float)
    cum_tp_v = (tp * vol).cumsum()
    cum_v = vol.cumsum().replace(0, np.nan)
    return (cum_tp_v / cum_v).ffill().to_numpy()


class NeutralVwapMrScalp(Strategy):
    """
    Neutral intraday-style mean reversion vs a running VWAP proxy; works on any bar size.
    """

    adx_period = 14
    adx_max = 26
    rsi_period = 7
    atr_period = 14
    vol_window = 20
    dist_atr = 0.85
    risk_atr = 1.0
    reward_atr = 1.3

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume

        self.adx = self.I(talib.ADX, high, low, close, self.adx_period)
        self.rsi = self.I(talib.RSI, close, self.rsi_period)
        self.atr = self.I(talib.ATR, high, low, close, self.atr_period)
        self.vol_sma = self.I(_rolling_mean, volume, self.vol_window)
        self.vwap = self.I(_vwap_approx, high, low, close, volume)

    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]
        vw = self.vwap[-1]
        if not np.isfinite(atr) or atr <= 0 or not np.isfinite(vw):
            return

        chop = self.adx[-1] < self.adx_max
        vol_ok = self.data.Volume[-1] > 0.8 * self.vol_sma[-1]

        if not self.position:
            if chop and vol_ok and price < vw - self.dist_atr * atr and self.rsi[-1] < 36:
                self.buy(sl=price - self.risk_atr * atr, tp=price + self.reward_atr * atr)
            elif chop and vol_ok and price > vw + self.dist_atr * atr and self.rsi[-1] > 64:
                self.sell(sl=price + self.risk_atr * atr, tp=price - self.reward_atr * atr)
            return

        if self.position.is_long:
            if price >= vw or self.rsi[-1] > 55:
                self.position.close()
        else:
            if price <= vw or self.rsi[-1] < 45:
                self.position.close()
