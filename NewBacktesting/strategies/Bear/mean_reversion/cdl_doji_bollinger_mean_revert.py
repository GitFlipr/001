"""
Doji in Bollinger extremes mean reversion.

Signals:
- Long when doji occurs below lower band (oversold)
- Short when doji occurs above upper band (overbought)
- Exit at middle band or opposite signal
"""
from __future__ import annotations

import numpy as np
import talib
from backtesting import Strategy


class CdlDojiBollingerMeanRevert(Strategy):
    bb_period = 20
    bb_dev = 2.0

    def init(self):
        upper, middle, lower = talib.BBANDS(
            self.data.Close,
            timeperiod=self.bb_period,
            nbdevup=self.bb_dev,
            nbdevdn=self.bb_dev,
            matype=0,
        )
        self.bb_u = self.I(lambda x: upper, self.data.Close)
        self.bb_m = self.I(lambda x: middle, self.data.Close)
        self.bb_l = self.I(lambda x: lower, self.data.Close)
        self.doji = self.I(
            talib.CDLDOJI,
            self.data.Open,
            self.data.High,
            self.data.Low,
            self.data.Close,
        )

    def next(self):
        if len(self.data) < self.bb_period + 10:
            return
        if np.isnan(self.bb_u[-1]) or np.isnan(self.bb_l[-1]) or np.isnan(self.bb_m[-1]):
            return
        close = float(self.data.Close[-1])
        doji = float(self.doji[-1]) != 0.0
        upper = float(self.bb_u[-1])
        lower = float(self.bb_l[-1])
        mid = float(self.bb_m[-1])

        long_sig = doji and close < lower
        short_sig = doji and close > upper

        if not self.position:
            if long_sig:
                self.buy()
            elif short_sig:
                self.sell()
            return

        if self.position.is_long:
            if close >= mid or short_sig:
                self.position.close()
        else:
            if close <= mid or long_sig:
                self.position.close()
