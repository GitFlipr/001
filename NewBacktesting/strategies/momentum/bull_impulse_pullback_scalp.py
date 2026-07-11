from __future__ import annotations

import numpy as np
import pandas as pd
from backtesting import Strategy
import talib


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


def _zscore(arr, window):
    s = pd.Series(arr, dtype=float)
    mu = s.rolling(window).mean()
    sd = s.rolling(window).std().replace(0, np.nan)
    return ((s - mu) / sd).fillna(0.0).to_numpy()


class BullImpulsePullbackScalp(Strategy):
    """
    Bull-regime intraday: buys shallow pullbacks in an uptrend; optional counter-trend fade on spikes.
    """

    fast_ema = 8
    slow_ema = 34
    rsi_period = 7
    vol_window = 30
    z_window = 40
    z_entry = 1.2
    atr_period = 14
    risk_atr = 1.2
    reward_atr = 1.6

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        volume = self.data.Volume

        self.ema_fast = self.I(talib.EMA, close, self.fast_ema)
        self.ema_slow = self.I(talib.EMA, close, self.slow_ema)
        self.rsi = self.I(talib.RSI, close, self.rsi_period)
        self.atr = self.I(talib.ATR, high, low, close, self.atr_period)
        self.vol_sma = self.I(_rolling_mean, volume, self.vol_window)
        self.ret_z = self.I(_zscore, pd.Series(close).pct_change().fillna(0.0).to_numpy(), self.z_window)

    def next(self):
        price = self.data.Close[-1]
        atr = self.atr[-1]
        if not np.isfinite(atr) or atr <= 0:
            return

        bull_trend = self.ema_fast[-1] > self.ema_slow[-1]
        vol_ok = self.data.Volume[-1] > self.vol_sma[-1]

        if not self.position:
            if bull_trend and vol_ok and self.ret_z[-1] < -self.z_entry and self.rsi[-1] < 40:
                self.buy(sl=price - self.risk_atr * atr, tp=price + self.reward_atr * atr)
            elif bull_trend and vol_ok and self.ret_z[-1] > self.z_entry and self.rsi[-1] > 68:
                self.sell(sl=price + self.risk_atr * atr, tp=price - 1.2 * atr)
            return

        if self.position.is_long:
            if self.rsi[-1] > 72 or self.ema_fast[-1] < self.ema_slow[-1]:
                self.position.close()
        else:
            if self.rsi[-1] < 35 or self.ema_fast[-1] > self.ema_slow[-1]:
                self.position.close()
