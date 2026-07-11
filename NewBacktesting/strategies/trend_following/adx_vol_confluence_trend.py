"""
Trend when ADX trend-strength and Bollinger bandwidth are in a favorable band.

See `Strategies/new/regime_prototypes/README.txt`.
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy
from backtesting.lib import crossover


class AdxVolConfluenceTrend(Strategy):
    fast = 20
    slow = 50
    adx_period = 14
    adx_min = 22.0
    bb_period = 20
    bb_dev = 2.0
    bw_lookback = 100
    bw_percentile_max = 75.0

    def init(self):
        c = self.data.Close
        self.ema_f = self.I(talib.EMA, c, timeperiod=self.fast)
        self.ema_s = self.I(talib.EMA, c, timeperiod=self.slow)
        self.adx = self.I(
            talib.ADX,
            self.data.High,
            self.data.Low,
            c,
            timeperiod=self.adx_period,
        )

        def _bb_width(close):
            arr = np.asarray(close, dtype=float)
            u, m, l = talib.BBANDS(
                arr,
                timeperiod=self.bb_period,
                nbdevup=self.bb_dev,
                nbdevdn=self.bb_dev,
                matype=0,
            )
            mid = np.where(np.abs(m) < 1e-12, np.nan, m)
            return (u - l) / mid

        self.bb_width = self.I(_bb_width, self.data.Close)

    def _range_ok(self) -> bool:
        i = len(self.data) - 1
        if i < self.slow + self.bw_lookback:
            return False
        bw = np.asarray(self.bb_width, dtype=float)
        start = max(0, i - self.bw_lookback)
        w = bw[start : i + 1]
        cur = w[-1]
        hist = w[:-1]
        hist = hist[np.isfinite(hist)]
        if not np.isfinite(cur) or hist.size < 15:
            return False
        p = 100.0 * float(np.mean(hist < cur))
        return p <= self.bw_percentile_max

    def next(self):
        if len(self.data) < self.slow + 2:
            return
        if np.isnan(self.adx[-1]) or self.adx[-1] < self.adx_min:
            if self.position:
                self.position.close()
            return
        if not self._range_ok():
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
