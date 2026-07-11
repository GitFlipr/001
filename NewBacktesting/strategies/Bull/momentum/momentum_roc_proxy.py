"""ROC momentum + volatility filter (cross-sectional proxy). From set_1/031."""
from backtesting import Strategy
import numpy as np
import talib


class MomentumRocProxy(Strategy):
    roc_period = 60
    atr_period = 14
    atr_max_pct = 0.05

    def init(self):
        self.roc = self.I(talib.ROC, self.data.Close, timeperiod=self.roc_period)
        self.atr = self.I(
            talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period
        )

    def next(self):
        if len(self.data) < self.roc_period + 2:
            return
        if np.isnan(self.roc[-1]) or np.isnan(self.atr[-1]):
            return
        c = self.data.Close[-1]
        vol_pct = self.atr[-1] / c if c else np.inf
        if vol_pct > self.atr_max_pct:
            return
        if not self.position:
            if self.roc[-1] > 0:
                self.buy()
            elif self.roc[-1] < 0:
                self.sell()
        else:
            if self.position.is_long and self.roc[-1] < 0:
                self.position.close()
            elif self.position.is_short and self.roc[-1] > 0:
                self.position.close()
