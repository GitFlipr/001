"""
Low-volatility regime strategies — built for compressed, slow-moving markets.

  LowVolCarryTrend      — slow trend following with tight risk in calm conditions
  LowVolBBMidReversion  — mean reversion to Bollinger midline when bands narrow
  LowVolROCMomentum     — rate-of-change momentum when volatility is compressed
  LowVolDualMASlow      — slow dual-MA crossover suited to low-noise environments
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, sma, rsi, atr, bollinger_bands, roc


class LowVolCarryTrend(Strategy):
    """
    Slow trend-following with position held until trend reverses.
    Only enters when ATR is below its median — avoids volatile periods.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.ema_p   = self.params.get("ema_period",  50)
        self.atr_p   = self.params.get("atr_period",  14)
        self.atr_pct = self.params.get("atr_quantile", 0.4)  # below this = low vol

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, h, l = df["close"], df["high"], df["low"]

        ema_l  = ema(c, self.ema_p)
        atr_l  = atr(h, l, c, self.atr_p)
        low_v  = atr_l < atr_l.rolling(self.atr_p * 6).quantile(self.atr_pct)

        sig = pd.Series(0, index=df.index)
        in_pos = 0
        for i in range(len(df)):
            if in_pos == 1:
                if c.iloc[i] < ema_l.iloc[i]:
                    in_pos = 0
                else:
                    sig.iloc[i] = 1
            elif in_pos == -1:
                if c.iloc[i] > ema_l.iloc[i]:
                    in_pos = 0
                else:
                    sig.iloc[i] = -1
            else:
                if low_v.iloc[i]:
                    if c.iloc[i] > ema_l.iloc[i]:
                        in_pos = 1
                        sig.iloc[i] = 1
                    elif c.iloc[i] < ema_l.iloc[i]:
                        in_pos = -1
                        sig.iloc[i] = -1
        return pd.DataFrame({"signal": sig})


class LowVolBBMidReversion(Strategy):
    """
    When Bollinger Bands are narrow (low BBW), fade moves away from midline.
    Long below mid when BBW is tight; short above mid.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.bb_p    = self.params.get("bb_period",  20)
        self.bb_std  = self.params.get("bb_std",     1.5)
        self.bbw_q   = self.params.get("bbw_quantile", 0.35)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c = df["close"]

        upper, mid, lower = bollinger_bands(c, self.bb_p, self.bb_std)
        bbw      = upper - lower
        tight    = bbw < bbw.rolling(self.bb_p * 3).quantile(self.bbw_q)

        sig = pd.Series(0, index=df.index)
        in_pos = 0
        for i in range(len(df)):
            if in_pos == 1:
                if c.iloc[i] >= mid.iloc[i]:
                    in_pos = 0
                else:
                    sig.iloc[i] = 1
            elif in_pos == -1:
                if c.iloc[i] <= mid.iloc[i]:
                    in_pos = 0
                else:
                    sig.iloc[i] = -1
            else:
                if tight.iloc[i]:
                    if c.iloc[i] < lower.iloc[i]:
                        in_pos = 1
                        sig.iloc[i] = 1
                    elif c.iloc[i] > upper.iloc[i]:
                        in_pos = -1
                        sig.iloc[i] = -1
        return pd.DataFrame({"signal": sig})


class LowVolROCMomentum(Strategy):
    """
    Rate-of-change momentum only when volatility is low.
    Long on positive ROC; short on negative. Exit on sign flip.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.roc_p   = self.params.get("roc_period",  10)
        self.atr_p   = self.params.get("atr_period",  14)
        self.atr_q   = self.params.get("atr_quantile", 0.4)
        self.rsi_p   = self.params.get("rsi_period",  14)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, h, l = df["close"], df["high"], df["low"]

        roc_l  = roc(c, self.roc_p)
        atr_l  = atr(h, l, c, self.atr_p)
        low_v  = atr_l < atr_l.rolling(self.atr_p * 6).quantile(self.atr_q)
        rsi_l  = rsi(c, self.rsi_p)

        sig = pd.Series(0, index=df.index)
        sig[low_v & (roc_l > 0) & (rsi_l < 65)] =  1
        sig[low_v & (roc_l < 0) & (rsi_l > 35)] = -1
        return pd.DataFrame({"signal": sig})


class LowVolDualMASlow(Strategy):
    """
    Slow dual-MA crossover (50/100) with ATR low-vol filter.
    Low whipsaw risk because fast MA is already slow.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.fast   = self.params.get("fast_period",  50)
        self.slow   = self.params.get("slow_period", 100)
        self.atr_p  = self.params.get("atr_period",  14)
        self.atr_q  = self.params.get("atr_quantile", 0.45)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, h, l = df["close"], df["high"], df["low"]

        sma_f  = sma(c, self.fast)
        sma_s  = sma(c, self.slow)
        atr_l  = atr(h, l, c, self.atr_p)
        low_v  = atr_l < atr_l.rolling(self.atr_p * 6).quantile(self.atr_q)

        bull = (sma_f > sma_s) & low_v
        bear = (sma_f < sma_s) & low_v

        sig = pd.Series(0, index=df.index)
        sig[bull] =  1
        sig[bear] = -1
        return pd.DataFrame({"signal": sig})
