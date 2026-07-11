"""
High-volatility regime strategies — built for expanded ATR environments.

  HighVolATRBreakout    — trade breakouts only when ATR is elevated
  HighVolBollingerRide  — ride price outside Bollinger Bands in trending vol
  HighVolKeltnerSqueeze — Keltner/BB squeeze into a volatility expansion
  HighVolGapMomentum    — gap-and-go momentum on high-vol opens
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, sma, rsi, atr, bollinger_bands


class HighVolATRBreakout(Strategy):
    """
    Breakout trade gated on ATR being above its N-bar average.
    Long above rolling high; short below rolling low.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.lookback  = self.params.get("lookback",    20)
        self.atr_p     = self.params.get("atr_period",  14)
        self.atr_mult  = self.params.get("atr_mult",    1.2)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, h, l = df["close"], df["high"], df["low"]

        atr_l     = atr(h, l, c, self.atr_p)
        atr_avg   = atr_l.rolling(self.atr_p * 3).mean()
        high_vol  = atr_l > self.atr_mult * atr_avg

        roll_high = h.shift(1).rolling(self.lookback).max()
        roll_low  = l.shift(1).rolling(self.lookback).min()

        sig = pd.Series(0, index=df.index)
        sig[high_vol & (c > roll_high)] =  1
        sig[high_vol & (c < roll_low)]  = -1
        return pd.DataFrame({"signal": sig})


class HighVolBollingerRide(Strategy):
    """
    Ride price when it closes outside Bollinger Bands on high volatility.
    Enter in the direction of the breakout; exit when price returns inside.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.bb_p   = self.params.get("bb_period", 20)
        self.bb_std = self.params.get("bb_std",    2.0)
        self.atr_p  = self.params.get("atr_period", 14)
        self.atr_m  = self.params.get("atr_mult",   1.1)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, h, l = df["close"], df["high"], df["low"]

        upper, mid, lower = bollinger_bands(c, self.bb_p, self.bb_std)
        atr_l   = atr(h, l, c, self.atr_p)
        atr_avg = atr_l.rolling(self.atr_p * 3).mean()
        hi_vol  = atr_l > self.atr_m * atr_avg

        sig = pd.Series(0, index=df.index)
        position = 0
        for i in range(len(df)):
            if position == 1:
                sig.iloc[i] = 1
                if c.iloc[i] < mid.iloc[i]:
                    position = 0
                    sig.iloc[i] = 0
            elif position == -1:
                sig.iloc[i] = -1
                if c.iloc[i] > mid.iloc[i]:
                    position = 0
                    sig.iloc[i] = 0
            else:
                if hi_vol.iloc[i]:
                    if c.iloc[i] > upper.iloc[i]:
                        position = 1
                        sig.iloc[i] = 1
                    elif c.iloc[i] < lower.iloc[i]:
                        position = -1
                        sig.iloc[i] = -1
        return pd.DataFrame({"signal": sig})


class HighVolKeltnerSqueeze(Strategy):
    """
    Keltner/Bollinger squeeze into volatility expansion.
    When BBW < Keltner width (squeeze), wait. Enter in trend direction on expansion.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.bb_p    = self.params.get("bb_period",  20)
        self.bb_std  = self.params.get("bb_std",     2.0)
        self.kc_p    = self.params.get("kc_period",  20)
        self.kc_mult = self.params.get("kc_mult",    1.5)
        self.ema_p   = self.params.get("ema_period", 20)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, h, l = df["close"], df["high"], df["low"]

        upper_bb, _, lower_bb = bollinger_bands(c, self.bb_p, self.bb_std)
        bbw  = upper_bb - lower_bb

        kc_mid   = ema(c, self.kc_p)
        atr_l    = atr(h, l, c, self.kc_p)
        kc_upper = kc_mid + self.kc_mult * atr_l
        kc_lower = kc_mid - self.kc_mult * atr_l
        kcw      = kc_upper - kc_lower

        squeeze   = bbw < kcw
        expansion = ~squeeze & squeeze.shift(1).fillna(True)

        ema_l   = ema(c, self.ema_p)
        uptrend = c > ema_l

        sig = pd.Series(0, index=df.index)
        sig[expansion & uptrend]  =  1
        sig[expansion & ~uptrend] = -1
        return pd.DataFrame({"signal": sig})


class HighVolGapMomentum(Strategy):
    """
    Gap-and-go: enter in the gap direction when today's open gaps
    more than 0.5 * ATR from yesterday's close, confirmed by first-bar direction.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.atr_p    = self.params.get("atr_period", 14)
        self.gap_mult = self.params.get("gap_mult",   0.5)
        self.rsi_p    = self.params.get("rsi_period", 10)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, o, h, l = df["close"], df["open"], df["high"], df["low"]

        atr_l    = atr(h, l, c, self.atr_p)
        gap      = o - c.shift(1)
        gap_up   = gap >  self.gap_mult * atr_l
        gap_down = gap < -self.gap_mult * atr_l
        bull_bar = c > o
        bear_bar = c < o
        rsi_l    = rsi(c, self.rsi_p)

        sig = pd.Series(0, index=df.index)
        sig[gap_up   & bull_bar & (rsi_l < 75)] =  1
        sig[gap_down & bear_bar & (rsi_l > 25)] = -1
        return pd.DataFrame({"signal": sig})
