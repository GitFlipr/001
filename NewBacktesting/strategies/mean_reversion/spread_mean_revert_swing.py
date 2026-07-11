from __future__ import annotations

import numpy as np
import pandas as pd
from backtesting import Strategy
import talib


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


def _residual_zscore(close, baseline_period, z_window):
    c = pd.Series(close, dtype=float)
    baseline = c.rolling(int(baseline_period)).mean()
    resid = c - baseline
    mu = resid.rolling(int(z_window)).mean()
    sd = resid.rolling(int(z_window)).std().replace(0, np.nan)
    return ((resid - mu) / sd).fillna(0.0).to_numpy()


class SpreadMeanRevertSwing(Strategy):
    """
    Stat-arb-style swing on single series: fade wide z-scores of price vs a slow drifting mean.
    """

    baseline_period = 120
    z_window = 80
    z_entry = 2.05
    z_exit = 0.35
    atr_period = 14
    vol_window = 40
    risk_atr = 2.0
    reward_atr = 2.8

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume

        self.z = self.I(_residual_zscore, close, self.baseline_period, self.z_window)
        self.atr = self.I(talib.ATR, high, low, close, self.atr_period)
        self.vol_sma = self.I(_rolling_mean, volume, self.vol_window)

    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]
        if not np.isfinite(atr) or atr <= 0:
            return

        z = self.z[-1]
        vol_ok = self.data.Volume[-1] >= 0.9 * self.vol_sma[-1]

        if not self.position:
            if vol_ok and z < -self.z_entry:
                self.buy(sl=price - self.risk_atr * atr, tp=price + self.reward_atr * atr)
            elif vol_ok and z > self.z_entry:
                self.sell(sl=price + self.risk_atr * atr, tp=price - self.reward_atr * atr)
            return

        if self.position.is_long:
            if z > -self.z_exit:
                self.position.close()
        else:
            if z < self.z_exit:
                self.position.close()
