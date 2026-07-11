"""
Volume Price Trend (VPT) Strategy - From 117.
VPT = VPT_prev + Volume * (Close - Close_prev) / Close_prev.
Long when VPT rising, short when VPT falling.
"""
import numpy as np
import pandas as pd
from backtesting import Strategy
import talib


def _vpt_indicator(close_series, volume_series):
    """VPT cumulative."""
    c = pd.Series(close_series)
    v = pd.Series(volume_series)
    pct_change = c.pct_change()
    vpt = (v * pct_change).cumsum()
    return np.asarray(vpt)


class VolumePriceTrendStrategy(Strategy):
    """VPT: long when VPT rising (VPT > VPT MA), short when falling."""

    vpt_ma_period = 20

    def init(self):
        close = self.data.Close
        volume = self.data.Volume
        self.vpt = self.I(_vpt_indicator, close, volume)
        self.vpt_ma = self.I(lambda v: np.asarray(pd.Series(v).rolling(self.vpt_ma_period).mean()), self.vpt)

    def next(self):
        if len(self.data) < self.vpt_ma_period + 5:
            return
        if np.isnan(self.vpt[-1]) or np.isnan(self.vpt_ma[-1]):
            return

        vpt_rising = self.vpt[-1] > self.vpt_ma[-1]
        vpt_falling = self.vpt[-1] < self.vpt_ma[-1]
        vpt_cross_up = len(self.data) >= 2 and self.vpt[-2] <= self.vpt_ma[-2] and self.vpt[-1] > self.vpt_ma[-1]
        vpt_cross_down = len(self.data) >= 2 and self.vpt[-2] >= self.vpt_ma[-2] and self.vpt[-1] < self.vpt_ma[-1]

        if not self.position:
            if vpt_cross_up or vpt_rising:
                self.buy()
            elif vpt_cross_down or vpt_falling:
                self.sell()
        else:
            if self.position.is_long and vpt_cross_down:
                self.position.close()
            elif self.position.is_short and vpt_cross_up:
                self.position.close()
