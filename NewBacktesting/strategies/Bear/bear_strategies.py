"""
Bear regime strategies — designed for downtrending, risk-off markets.

  BearEMAShort          — short on EMA stack rejection with volume confirmation
  BearRSIOverextended   — fade rallies when RSI reaches overbought in a downtrend
  BearBreakdownPullback — short on breakdown below support with pullback entry
  BearMACDMomentum      — MACD death-cross momentum short with ATR trailing
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, sma, rsi, atr, macd


class BearEMAShort(Strategy):
    """
    Short when price is below a falling EMA stack (fast < slow < 200)
    and a bearish rejection candle forms on above-average volume.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.fast   = self.params.get("fast_period",  9)
        self.slow   = self.params.get("slow_period",  21)
        self.trend  = self.params.get("trend_period", 200)
        self.vol_p  = self.params.get("vol_period",   20)
        self.vol_m  = self.params.get("vol_mult",     1.2)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, o, h, v = df["close"], df["open"], df["high"], df["volume"]

        ema_f  = ema(c, self.fast)
        ema_s  = ema(c, self.slow)
        ema_t  = ema(c, self.trend)
        vol_a  = sma(v, self.vol_p)

        # Bear stack: fast < slow < trend
        bear_stack = (ema_f < ema_s) & (ema_s < ema_t)

        # Bearish rejection: price opened above EMA fast and closed below it
        rejection = (o > ema_f) & (c < ema_f) & (c < o)

        # Volume confirmation
        vol_ok = v > self.vol_m * vol_a

        sig = pd.Series(0, index=df.index)
        sig[bear_stack & rejection & vol_ok] = -1
        # Exit: close above fast EMA
        sig[(c > ema_f) & (sig == 0)] = 0
        return pd.DataFrame({"signal": sig})


class BearRSIOverextended(Strategy):
    """
    Short counter-trend rallies in a downtrend.
    Enters short when RSI rallies above 60 while price is below the 50 EMA,
    exits when RSI drops back below 45.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.ema_p    = self.params.get("ema_period",  50)
        self.rsi_p    = self.params.get("rsi_period",  14)
        self.rsi_ent  = self.params.get("rsi_entry",   60)
        self.rsi_ext  = self.params.get("rsi_exit",    45)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c = df["close"]

        ema_l  = ema(c, self.ema_p)
        rsi_l  = rsi(c, self.rsi_p)

        downtrend = c < ema_l
        overbought_rally = rsi_l > self.rsi_ent
        rsi_exhausted    = rsi_l < self.rsi_ext

        sig = pd.Series(0, index=df.index)
        in_short = False
        for i in range(len(df)):
            if in_short:
                if rsi_exhausted.iloc[i]:
                    in_short = False
                else:
                    sig.iloc[i] = -1
            else:
                if downtrend.iloc[i] and overbought_rally.iloc[i]:
                    in_short = True
                    sig.iloc[i] = -1
        return pd.DataFrame({"signal": sig})


class BearBreakdownPullback(Strategy):
    """
    Short on pullback after a support breakdown.
    Breakdown = close below N-bar low. Pullback = close retraces toward
    broken level but fails to reclaim it.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.lookback  = self.params.get("lookback",    20)
        self.pullback  = self.params.get("pullback_p",   5)
        self.atr_p     = self.params.get("atr_period",  14)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, h, l = df["close"], df["high"], df["low"]

        support      = l.shift(1).rolling(self.lookback).min()
        broke_down   = (c.shift(1) > support.shift(1)) & (c < support)
        broke_flag   = broke_down.astype(int).rolling(self.pullback).max().astype(bool)

        # Pullback: price rises back toward broken support but stays below it
        recent_high  = h.rolling(self.pullback).max()
        pullback_hit = (recent_high >= support * 0.99) & (c < support)

        sig = pd.Series(0, index=df.index)
        sig[broke_flag & pullback_hit] = -1
        return pd.DataFrame({"signal": sig})


class BearMACDMomentum(Strategy):
    """
    MACD death-cross short: enter when MACD crosses below signal in a downtrend.
    Exit when histogram turns positive for two consecutive bars.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.trend_p = self.params.get("trend_period", 50)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c = df["close"]

        ema_t = ema(c, self.trend_p)
        macd_l, signal_l, hist_l = macd(c)

        downtrend    = c < ema_t
        death_cross  = (macd_l < signal_l) & (macd_l.shift(1) >= signal_l.shift(1))
        hist_pos2    = (hist_l > 0) & (hist_l.shift(1) > 0)

        sig = pd.Series(0, index=df.index)
        in_short = False
        for i in range(len(df)):
            if in_short:
                if hist_pos2.iloc[i]:
                    in_short = False
                else:
                    sig.iloc[i] = -1
            else:
                if downtrend.iloc[i] and death_cross.iloc[i]:
                    in_short = True
                    sig.iloc[i] = -1
        return pd.DataFrame({"signal": sig})
