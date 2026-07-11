"""
XRP template: ATR band breakout with volume confirmation (liquid alt, event-sensitive).
Run only on XRP OHLCV; parameters should be re-tuned — this is a starting scaffold.

Not financial advice.
"""
import numpy as np
import talib
from backtesting import Strategy


class XrpVolBreakoutStrategy(Strategy):
    """
    Breakout of prior N-bar high with volume > SMA(vol) * vol_mult.
    Exit: opposite breakout or midline (EMA) cross.
    """

    ema_mid = 20
    breakout_lookback = 10
    vol_ma = 20
    vol_mult = 1.2
    atr_exit = 14

    def init(self):
        c = self.data.Close
        h, l = self.data.High, self.data.Low
        v = self.data.Volume.astype(float)
        self.ema = self.I(talib.EMA, c, timeperiod=self.ema_mid)
        self.vol_ma = self.I(talib.SMA, v, timeperiod=self.vol_ma)
        self.atr = self.I(talib.ATR, h, l, c, timeperiod=self.atr_exit)

    def next(self):
        n = max(self.breakout_lookback, self.vol_ma, self.ema_mid) + 2
        if len(self.data) < n:
            return
        c, h_i, l_i = self.data.Close[-1], self.data.High, self.data.Low
        v = float(self.data.Volume[-1])
        hh = max(float(h_i[i]) for i in range(-self.breakout_lookback - 1, -1))
        ll = min(float(l_i[i]) for i in range(-self.breakout_lookback - 1, -1))
        vol_ok = not np.isnan(self.vol_ma[-1]) and v >= self.vol_ma[-1] * self.vol_mult

        if not self.position:
            if vol_ok and c > hh:
                self.buy()
            elif vol_ok and c < ll:
                self.sell()
        else:
            if self.position.is_long:
                if c < self.ema[-1] or c < ll:
                    self.position.close()
            elif self.position.is_short:
                if c > self.ema[-1] or c > hh:
                    self.position.close()
