"""
Multi-signal "ensemble" gate: trade only when several weakly-correlated conditions align.
Inspired by *ideas* discussed in quant literature (many weak predictors, risk control) —
this is a toy template, not a replica of any proprietary fund.

Not financial advice.
"""
import numpy as np
import talib
from backtesting import Strategy


class MultiSignalVoteStrategy(Strategy):
    """
    Vote over:
      TREND: close > SMA(sma_len)
      MOM: ROC(roc_len) > 0 (long) or < 0 (short)
      CALM: ATR/price below its own SMA (avoid manic spikes) OR invert for breakout variant

    Long if trend & mom & calm; exit on trend break or 2-of-3 failure next bar.
    """

    sma_len = 60
    roc_len = 20
    atr_period = 14
    calm_lookback = 60
    votes_needed = 2  # require 2 of 3 (trend / momentum / calm)

    def init(self):
        c = self.data.Close
        h, l = self.data.High, self.data.Low
        self.sma = self.I(talib.SMA, c, timeperiod=self.sma_len)
        self.roc = self.I(talib.ROC, c, timeperiod=self.roc_len)
        self.atr = self.I(talib.ATR, h, l, c, timeperiod=self.atr_period)

    def _calm(self) -> bool:
        c = float(self.data.Close[-1])
        if c <= 0:
            return False
        atr_pct = self.atr[-1] / c
        if len(self.data) < self.calm_lookback + 5 or np.isnan(atr_pct):
            return False
        # Simple: ATR% below its trailing mean => relatively calm
        start = max(0, len(self.data) - self.calm_lookback)
        hist = []
        for i in range(start, len(self.data)):
            cl = float(self.data.Close[i])
            if cl > 0 and not np.isnan(self.atr[i]):
                hist.append(self.atr[i] / cl)
        if not hist:
            return False
        return atr_pct <= float(np.nanmean(hist)) * 1.15

    def next(self):
        if len(self.data) < self.sma_len + self.roc_len + 5:
            return
        if np.isnan(self.sma[-1]) or np.isnan(self.roc[-1]):
            return
        c = self.data.Close[-1]
        trend_long = c > self.sma[-1]
        trend_short = c < self.sma[-1]
        mom_long = self.roc[-1] > 0
        mom_short = self.roc[-1] < 0
        calm = self._calm()

        v_long = int(trend_long) + int(mom_long) + int(calm)
        v_short = int(trend_short) + int(mom_short) + int(calm)

        if not self.position:
            if v_long >= self.votes_needed:
                self.buy()
            elif v_short >= self.votes_needed:
                self.sell()
        else:
            if self.position.is_long and (not trend_long or not mom_long):
                self.position.close()
            elif self.position.is_short and (not trend_short or not mom_short):
                self.position.close()
