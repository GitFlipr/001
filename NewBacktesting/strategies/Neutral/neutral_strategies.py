"""
Neutral / range-bound regime strategies.

  NeutralMeanReversionBand  — fade extremes within Bollinger Bands
  NeutralRSIReversion       — RSI oscillator mean reversion in choppy markets
  NeutralDualThreshold      — long/short on price touching channel boundaries
  NeutralVWAPReversion      — intraday VWAP mean-reversion
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, sma, rsi, bollinger_bands


class NeutralMeanReversionBand(Strategy):
    """
    Fade the Bollinger Band extremes when ADX is low (range-bound).
    Long at lower band, short at upper band. Exit at middle band.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.bb_p   = self.params.get("bb_period", 20)
        self.bb_std = self.params.get("bb_std",    2.0)
        self.adx_p  = self.params.get("adx_period", 14)
        self.adx_th = self.params.get("adx_thresh", 25)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, h, l = df["close"], df["high"], df["low"]

        upper, mid, lower = bollinger_bands(c, self.bb_p, self.bb_std)

        # ADX proxy: smoothed TR / price as trend strength
        tr = pd.concat([h - l,
                        (h - c.shift()).abs(),
                        (l - c.shift()).abs()], axis=1).max(axis=1)
        adx_proxy = tr.rolling(self.adx_p).mean() / c
        ranging   = adx_proxy < adx_proxy.rolling(self.adx_p * 2).quantile(0.4)

        sig = pd.Series(0, index=df.index)
        position = 0
        for i in range(len(df)):
            if position == 1:
                if c.iloc[i] >= mid.iloc[i]:
                    position = 0
                else:
                    sig.iloc[i] = 1
            elif position == -1:
                if c.iloc[i] <= mid.iloc[i]:
                    position = 0
                else:
                    sig.iloc[i] = -1
            else:
                if ranging.iloc[i]:
                    if c.iloc[i] <= lower.iloc[i]:
                        position = 1
                        sig.iloc[i] = 1
                    elif c.iloc[i] >= upper.iloc[i]:
                        position = -1
                        sig.iloc[i] = -1
        return pd.DataFrame({"signal": sig})


class NeutralRSIReversion(Strategy):
    """
    Pure RSI oscillator mean reversion.
    Long when RSI < oversold, exit at 50. Short when RSI > overbought, exit at 50.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.rsi_p = self.params.get("rsi_period",  14)
        self.os    = self.params.get("oversold",     30)
        self.ob    = self.params.get("overbought",   70)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        rsi_l = rsi(df["close"], self.rsi_p)

        sig = pd.Series(0, index=df.index)
        position = 0
        for i in range(len(df)):
            if position == 1:
                if rsi_l.iloc[i] >= 50:
                    position = 0
                else:
                    sig.iloc[i] = 1
            elif position == -1:
                if rsi_l.iloc[i] <= 50:
                    position = 0
                else:
                    sig.iloc[i] = -1
            else:
                if rsi_l.iloc[i] < self.os:
                    position = 1
                    sig.iloc[i] = 1
                elif rsi_l.iloc[i] > self.ob:
                    position = -1
                    sig.iloc[i] = -1
        return pd.DataFrame({"signal": sig})


class NeutralDualThreshold(Strategy):
    """
    Donchian channel mean reversion.
    Long when price touches the lower N-bar channel; short at upper channel.
    Exit at the midpoint.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.ch_p = self.params.get("channel_period", 20)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, h, l = df["close"], df["high"], df["low"]

        ch_high = h.rolling(self.ch_p).max().shift(1)
        ch_low  = l.rolling(self.ch_p).min().shift(1)
        mid     = (ch_high + ch_low) / 2

        sig = pd.Series(0, index=df.index)
        position = 0
        for i in range(len(df)):
            if position == 1:
                if c.iloc[i] >= mid.iloc[i]:
                    position = 0
                else:
                    sig.iloc[i] = 1
            elif position == -1:
                if c.iloc[i] <= mid.iloc[i]:
                    position = 0
                else:
                    sig.iloc[i] = -1
            else:
                if c.iloc[i] <= ch_low.iloc[i]:
                    position = 1
                    sig.iloc[i] = 1
                elif c.iloc[i] >= ch_high.iloc[i]:
                    position = -1
                    sig.iloc[i] = -1
        return pd.DataFrame({"signal": sig})


class NeutralVWAPReversion(Strategy):
    """
    Intraday VWAP mean-reversion.
    Long when price is more than 1 ATR below VWAP; short when 1 ATR above.
    Exit at VWAP.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.atr_p     = self.params.get("atr_period",    14)
        self.atr_mult  = self.params.get("atr_mult",       1.0)
        self.vwap_win  = self.params.get("vwap_window",  390)  # ~1 trading day of 1m bars

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c, h, l, v = df["close"], df["high"], df["low"], df["volume"]

        typical = (h + l + c) / 3
        win = min(self.vwap_win, len(df))
        vwap = (typical * v).rolling(win).sum() / v.rolling(win).sum()

        tr = pd.concat([h - l,
                        (h - c.shift()).abs(),
                        (l - c.shift()).abs()], axis=1).max(axis=1)
        atr_l = tr.rolling(self.atr_p).mean()
        band  = self.atr_mult * atr_l

        sig = pd.Series(0, index=df.index)
        position = 0
        for i in range(len(df)):
            if position == 1:
                if c.iloc[i] >= vwap.iloc[i]:
                    position = 0
                else:
                    sig.iloc[i] = 1
            elif position == -1:
                if c.iloc[i] <= vwap.iloc[i]:
                    position = 0
                else:
                    sig.iloc[i] = -1
            else:
                if c.iloc[i] < vwap.iloc[i] - band.iloc[i]:
                    position = 1
                    sig.iloc[i] = 1
                elif c.iloc[i] > vwap.iloc[i] + band.iloc[i]:
                    position = -1
                    sig.iloc[i] = -1
        return pd.DataFrame({"signal": sig})
