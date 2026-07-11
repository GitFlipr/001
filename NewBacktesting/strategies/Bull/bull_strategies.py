"""
Bull regime strategies — designed for uptrending, risk-on markets.

  BullEMACross          — classic fast/slow EMA crossover filtered by 200 EMA trend
  BullRSIPullback       — buy RSI dips to oversold in a confirmed uptrend
  BullBreakoutReentry   — re-enter on first pullback after a breakout
  BullVolumeMomentum    — accumulation signal: rising price + expanding volume
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, sma, rsi, atr, macd


class BullEMACross(Strategy):
    """
    Long when the fast EMA crosses above the slow EMA while price is
    above the 200-period trend EMA. Exit on reverse cross.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.fast   = self.params.get("fast_period",  9)
        self.slow   = self.params.get("slow_period",  21)
        self.trend  = self.params.get("trend_period", 200)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c = df["close"]

        ema_f = ema(c, self.fast)
        ema_s = ema(c, self.slow)
        ema_t = ema(c, self.trend)

        bull_cross = (ema_f > ema_s) & (ema_f.shift(1) <= ema_s.shift(1))
        bear_cross = (ema_f < ema_s) & (ema_f.shift(1) >= ema_s.shift(1))
        uptrend    = c > ema_t

        sig = pd.Series(0, index=df.index)
        in_long = False
        for i in range(len(df)):
            if in_long:
                if bear_cross.iloc[i]:
                    in_long = False
                else:
                    sig.iloc[i] = 1
            else:
                if bull_cross.iloc[i] and uptrend.iloc[i]:
                    in_long = True
                    sig.iloc[i] = 1
        return pd.DataFrame({"signal": sig})


class BullRSIPullback(Strategy):
    """
    Buy when RSI dips below oversold threshold while trend is up.
    Exit when RSI reaches overbought or price closes below trend EMA.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.ema_p   = self.params.get("ema_period",  50)
        self.rsi_p   = self.params.get("rsi_period",  14)
        self.os      = self.params.get("oversold",    35)
        self.ob      = self.params.get("overbought",  65)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c = df["close"]

        ema_l = ema(c, self.ema_p)
        rsi_l = rsi(c, self.rsi_p)

        uptrend = c > ema_l

        sig = pd.Series(0, index=df.index)
        in_long = False
        for i in range(len(df)):
            if in_long:
                if rsi_l.iloc[i] > self.ob or c.iloc[i] < ema_l.iloc[i]:
                    in_long = False
                else:
                    sig.iloc[i] = 1
            else:
                if uptrend.iloc[i] and rsi_l.iloc[i] < self.os:
                    in_long = True
                    sig.iloc[i] = 1
        return pd.DataFrame({"signal": sig})


class BullBreakoutReentry(Strategy):
    """
    Enter long on the first pullback after price breaks above a rolling high.
    Pullback defined as: N bars after the breakout bar, close is still
    above the breakout level.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.lookback = self.params.get("lookback",   20)
        self.reentry  = self.params.get("reentry_p",   5)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, l = df["close"], df["low"]

        resistance    = c.shift(1).rolling(self.lookback).max()
        breakout      = (c.shift(1) <= resistance.shift(1)) & (c > resistance)
        broke_flag    = breakout.astype(int).rolling(self.reentry).max().astype(bool)

        # Pullback: price dips but stays above the broken resistance
        recent_low    = l.rolling(self.reentry).min()
        pulled_back   = (recent_low < c) & (recent_low >= resistance * 0.995)

        sig = pd.Series(0, index=df.index)
        sig[broke_flag & pulled_back] = 1
        return pd.DataFrame({"signal": sig})


class BullVolumeMomentum(Strategy):
    """
    Accumulation signal: close higher than previous close AND volume
    is above its N-bar average for at least M consecutive bars.
    Exits when either condition breaks.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.vol_p      = self.params.get("vol_period",     20)
        self.vol_m      = self.params.get("vol_mult",        1.1)
        self.confirm    = self.params.get("confirm_bars",     2)
        self.ema_p      = self.params.get("ema_period",      50)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, v = df["close"], df["volume"]

        vol_avg  = sma(v, self.vol_p)
        ema_l    = ema(c, self.ema_p)

        up_close = (c > c.shift(1)).astype(int)
        vol_up   = (v > self.vol_m * vol_avg).astype(int)
        both     = (up_close & vol_up)
        consec   = both.rolling(self.confirm).min().astype(bool)

        sig = pd.Series(0, index=df.index)
        in_long = False
        for i in range(len(df)):
            if in_long:
                # Exit: price crosses below trend EMA or volume dries up
                if c.iloc[i] < ema_l.iloc[i] or v.iloc[i] < vol_avg.iloc[i] * 0.8:
                    in_long = False
                else:
                    sig.iloc[i] = 1
            else:
                if consec.iloc[i] and c.iloc[i] > ema_l.iloc[i]:
                    in_long = True
                    sig.iloc[i] = 1
        return pd.DataFrame({"signal": sig})
