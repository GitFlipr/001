"""Rolling VWAP pivot (typical price * volume) for mean-reversion / reclaim entries."""

import numpy as np
from backtesting import Strategy


class FluxVWAPPivotStrategy(Strategy):
    window = 48

    def init(self):
        tp = (self.data.High + self.data.Low + self.data.Close) / 3.0
        vol = self.data.Volume
        w = self.window

        def rolling_vwap(typical, volume):
            out = np.full(len(typical), np.nan)
            tv = typical * volume
            for i in range(len(typical)):
                j0 = max(0, i - w + 1)
                vsum = np.nansum(volume[j0 : i + 1])
                if vsum > 0:
                    out[i] = np.nansum(tv[j0 : i + 1]) / vsum
            return out

        self.vwap = self.I(rolling_vwap, tp, vol)

    def next(self):
        if len(self.data) < self.window + 2:
            return
        if np.isnan(self.vwap[-1]) or np.isnan(self.vwap[-2]):
            return

        below_then_above = self.data.Close[-2] < self.vwap[-2] and self.data.Close[-1] > self.vwap[-1]
        above_then_below = self.data.Close[-2] > self.vwap[-2] and self.data.Close[-1] < self.vwap[-1]

        if below_then_above and not self.position:
            self.buy()
        elif self.position and above_then_below:
            self.position.close()
