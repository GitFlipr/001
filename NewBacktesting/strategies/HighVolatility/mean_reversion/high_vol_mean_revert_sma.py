"""
Mean-reversion toward SMA when volatility is *stressed* (high ATR% vs history).

See `strategy_storage/regime_prototypes/README.txt` for how this folder is used.
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy


class HighVolMeanRevertSma(Strategy):
    sma_period = 50
    atr_period = 14
    vol_lookback = 120
    vol_percentile_min = 70.0
    entry_atr_mult = 1.25

    def init(self):
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_period)
        self.atr = self.I(
            talib.ATR,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.atr_period,
        )

    def _stress_regime(self) -> bool:
        i = len(self.data) - 1
        if i < self.sma_period + self.vol_lookback:
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
        return p >= self.vol_percentile_min

    def next(self):
        if len(self.data) < self.sma_period + 2:
            return
        c = float(self.data.Close[-1])
        s = float(self.sma[-1])
        a = float(self.atr[-1])
        if any(map(np.isnan, (c, s, a))):
            return
        if not self._stress_regime():
            if self.position:
                self.position.close()
            return
        dev = self.entry_atr_mult * a
        if not self.position:
            if c > s + dev:
                self.sell()
            elif c < s - dev:
                self.buy()
        else:
            if self.position.is_long and c >= s:
                self.position.close()
            elif self.position.is_short and c <= s:
                self.position.close()
