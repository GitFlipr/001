"""EMA mid + ATR bands; breakout with volume. From set_2/053."""
import numpy as np
import talib
from backtesting import Strategy


class KeltnerBreakoutVol(Strategy):
    ema_period = 20
    atr_period = 10
    atr_mult = 2.0
    vol_ma_period = 20

    def init(self):
        self.mid = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        self.atr = self.I(
            talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period
        )
        self.vol_ma_ind = self.I(talib.SMA, self.data.Volume.astype(float), timeperiod=self.vol_ma_period)

    def next(self):
        if len(self.data) < max(self.ema_period, self.atr_period, self.vol_ma_period) + 1:
            return
        upper = self.mid[-1] + self.atr_mult * self.atr[-1]
        lower = self.mid[-1] - self.atr_mult * self.atr[-1]
        c = self.data.Close[-1]
        vol_ok = float(self.data.Volume[-1]) > self.vol_ma_ind[-1]
        if np.isnan(upper):
            return
        if not self.position:
            if vol_ok and c > upper:
                self.buy()
            elif vol_ok and c < lower:
                self.sell()
        else:
            if self.position.is_long and c < self.mid[-1]:
                self.position.close()
            elif self.position.is_short and c > self.mid[-1]:
                self.position.close()
