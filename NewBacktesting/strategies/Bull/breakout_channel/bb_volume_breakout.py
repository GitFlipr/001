"""Bollinger breakout + volume vs MA. From set_1/027."""
from backtesting import Strategy
import numpy as np
import talib


class BBVolumeBreakout(Strategy):
    bb_period = 20
    bb_dev = 2.0
    vol_ma_period = 20

    def init(self):
        u, m, l = self.I(
            talib.BBANDS,
            self.data.Close,
            timeperiod=self.bb_period,
            nbdevup=self.bb_dev,
            nbdevdn=self.bb_dev,
            matype=0,
        )
        self.bb_u, self.bb_m, self.bb_l = u, m, l
        self.vol_ma_ind = self.I(talib.SMA, self.data.Volume.astype(float), timeperiod=self.vol_ma_period)

    def next(self):
        if len(self.data) < max(self.bb_period, self.vol_ma_period) + 1:
            return
        c = self.data.Close[-1]
        if np.isnan(self.bb_u[-1]):
            return
        surge = float(self.data.Volume[-1]) > self.vol_ma_ind[-1]
        if not self.position:
            if surge and c > self.bb_u[-1]:
                self.buy()
            elif surge and c < self.bb_l[-1]:
                self.sell()
        else:
            if self.position.is_long and c < self.bb_m[-1]:
                self.position.close()
            elif self.position.is_short and c > self.bb_m[-1]:
                self.position.close()
