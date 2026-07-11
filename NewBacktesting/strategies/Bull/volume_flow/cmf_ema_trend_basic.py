"""CMF + EMA trend follower (TA-Lib EMA + numpy CMF; no pandas_ta)."""

import numpy as np
import talib
from backtesting import Strategy


def _cmf(high, low, close, volume, length: int):
    h = np.asarray(high, dtype=float)
    l = np.asarray(low, dtype=float)
    c = np.asarray(close, dtype=float)
    v = np.asarray(volume, dtype=float)
    n = len(c)
    out = np.full(n, np.nan)
    rng = np.maximum(h - l, 1e-12)
    mfv = ((c - l) - (h - c)) / rng * v
    for i in range(length, n):
        j0 = i - length + 1
        vs = np.sum(v[j0 : i + 1])
        out[i] = np.sum(mfv[j0 : i + 1]) / max(vs, 1e-12)
    return out


class PandasTaCmfEmaTrendBasic(Strategy):
    ema_fast = 20
    ema_slow = 100
    cmf_len = 20
    cmf_min = 0.05

    def init(self):
        self.ema_f = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_fast)
        self.ema_s = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_slow)
        L = self.cmf_len

        def cmf_wrap(h, l, c, v):
            return _cmf(h, l, c, v, L)

        self.cmf = self.I(
            cmf_wrap,
            self.data.High,
            self.data.Low,
            self.data.Close,
            self.data.Volume,
        )

    def next(self):
        if len(self.data) < max(self.ema_slow, self.cmf_len) + 5:
            return
        ef = float(self.ema_f[-1])
        es = float(self.ema_s[-1])
        cmf = float(self.cmf[-1])
        c = float(self.data.Close[-1])
        if any(np.isnan(x) for x in (ef, es, cmf)):
            return

        up = ef > es and c > es and cmf >= self.cmf_min
        dn = ef < es and c < es and cmf <= -self.cmf_min

        if not self.position:
            if up:
                self.buy()
            elif dn:
                self.sell()
        else:
            if self.position.is_long and cmf < 0:
                self.position.close()
            elif self.position.is_short and cmf > 0:
                self.position.close()
