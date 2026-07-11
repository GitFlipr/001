from __future__ import annotations

import numpy as np
import pandas as pd
from backtesting import Strategy
import talib


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


def _true_range_pct(h, l, c):
    hh = pd.Series(h)
    ll = pd.Series(l)
    cc = pd.Series(c)
    prev_c = cc.shift(1)
    tr = pd.concat([hh - ll, (hh - prev_c).abs(), (ll - prev_c).abs()], axis=1).max(axis=1)
    return (tr / cc.replace(0, np.nan)).fillna(0.0).to_numpy()


def _tr_spike_ratio(h, l, c, short_w, base_w):
    trp = _true_range_pct(h, l, c)
    s = pd.Series(trp).rolling(int(short_w)).mean()
    b = pd.Series(trp).rolling(int(base_w)).mean().replace(0, np.nan)
    return (s / b).fillna(0.0).to_numpy()


class VolSpikeFadeScalp(Strategy):
    """
    High-volatility intraday: fade extremes after a volatility spike versus a smoothed baseline.
    """

    tr_window = 5
    base_window = 60
    spike_mult = 1.35
    rsi_period = 7
    atr_period = 14
    vol_window = 30
    risk_atr = 1.1
    reward_atr = 1.5

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume

        self.spike_ratio = self.I(_tr_spike_ratio, high, low, close, self.tr_window, self.base_window)
        self.rsi = self.I(talib.RSI, close, self.rsi_period)
        self.atr = self.I(talib.ATR, high, low, close, self.atr_period)
        self.vol_sma = self.I(_rolling_mean, volume, self.vol_window)

    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]
        if not np.isfinite(atr) or atr <= 0:
            return

        spike = self.spike_ratio[-1] > self.spike_mult
        vol_ok = self.data.Volume[-1] > self.vol_sma[-1]

        if not self.position:
            if spike and vol_ok and self.rsi[-1] > 72:
                self.sell(sl=price + self.risk_atr * atr, tp=price - self.reward_atr * atr)
            elif spike and vol_ok and self.rsi[-1] < 28:
                self.buy(sl=price - self.risk_atr * atr, tp=price + self.reward_atr * atr)
            return

        if self.position.is_short:
            if self.rsi[-1] < 42:
                self.position.close()
        else:
            if self.rsi[-1] > 58:
                self.position.close()
