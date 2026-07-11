"""
EMA crossover only in a *calm* volatility regime (ATR% below a rolling percentile).

Motivation (survey / practice, not a one-to-one HMM fit):
- Hamilton-style Markov switching and HMM regime models treat volatility as
  state-dependent; many applied papers use a latent *high/low vol* split.
- Industry write-ups often use regime detection as a *risk filter* on top of a simple rule.

This file uses a lightweight proxy: current ATR/close vs its distribution over
`vol_lookback` bars. No scipy/hmmlearn dependency — good for fast iteration in
your backtester.

Storage: not wired to Master_Bot live bots — copy into your backtest strategy
package or import by path when running research backtests.
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy
from backtesting.lib import crossover


class VolRegimeGatedEmaCross(Strategy):
    fast = 20
    slow = 50
    atr_period = 14
    vol_lookback = 120
    vol_percentile_max = 55.0

    def init(self):
        self.ema_f = self.I(talib.EMA, self.data.Close, timeperiod=self.fast)
        self.ema_s = self.I(talib.EMA, self.data.Close, timeperiod=self.slow)
        self.atr = self.I(
            talib.ATR,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.atr_period,
        )

    def _calm_regime(self) -> bool:
        i = len(self.data) - 1
        if i < self.slow + self.vol_lookback:
            return False
        close = np.asarray(self.data.Close, dtype=float)
        atr = np.asarray(self.atr, dtype=float)
        start = max(0, i - self.vol_lookback)
        window_c = close[start : i + 1]
        window_a = atr[start : i + 1]
        with np.errstate(divide="ignore", invalid="ignore"):
            atr_pct = np.where(window_c > 0, 100.0 * window_a / window_c, np.nan)
        cur = atr_pct[-1]
        hist = atr_pct[:-1]
        hist = hist[np.isfinite(hist)]
        if not np.isfinite(cur) or hist.size < 20:
            return False
        p = 100.0 * float(np.mean(hist < cur))
        return p <= self.vol_percentile_max

    def next(self):
        if len(self.data) < self.slow + 2:
            return
        if np.isnan(self.ema_f[-1]) or np.isnan(self.ema_s[-1]):
            return
        if not self._calm_regime():
            if self.position:
                self.position.close()
            return
        if not self.position:
            if crossover(self.ema_f, self.ema_s):
                self.buy()
            elif crossover(self.ema_s, self.ema_f):
                self.sell()
        else:
            if self.position.is_long and crossover(self.ema_s, self.ema_f):
                self.position.close()
            elif self.position.is_short and crossover(self.ema_f, self.ema_s):
                self.position.close()
