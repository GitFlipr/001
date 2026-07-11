"""
Moon Dev strategy suite — migrated to backtest.strategies.base.Strategy.

Eight strategies ported from the legacy backtesting-library versions:
  NanosecondLiquidity   — spread/imbalance HFT-style mean reversion
  NicheConcentration    — EMA breakout + RSI + volume confluence
  CascadeWeighting      — adaptive cascade entries with ADX gating
  SynergisticConfluence — 6-signal confluence with SuperTrend + Fib
  KalmanSentiment       — Kalman-filtered rate-of-change momentum
  KellyFractional       — Kelly criterion periodic rebalancing
  BullishSqueeze        — Bollinger Band squeeze breakout (long only)
  EarningsPrelude       — SMA + RSI + volume momentum (long only)
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, sma, rsi, atr, macd, bollinger_bands


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _kalman(series: np.ndarray, Q: float = 0.01, R: float = 0.05) -> np.ndarray:
    """Univariate Kalman filter."""
    n = len(series)
    out = np.zeros(n)
    x, P = series[0], 1.0
    out[0] = x
    for i in range(1, n):
        x_p = x
        P_p = P + Q
        K = P_p / (P_p + R)
        x = x_p + K * (series[i] - x_p)
        P = (1 - K) * P_p
        out[i] = x
    return out


def _supertrend(high: pd.Series, low: pd.Series, close: pd.Series,
                atr_vals: pd.Series, mult: float = 3.0) -> pd.Series:
    hl2 = (high + low) / 2
    upper = hl2 + mult * atr_vals
    lower = hl2 - mult * atr_vals
    st = pd.Series(np.nan, index=close.index)
    direction = pd.Series(1, index=close.index)
    st.iloc[0] = lower.iloc[0]
    for i in range(1, len(close)):
        if close.iloc[i] > upper.iloc[i - 1]:
            direction.iloc[i] = 1
        elif close.iloc[i] < lower.iloc[i - 1]:
            direction.iloc[i] = -1
        else:
            direction.iloc[i] = direction.iloc[i - 1]
            if direction.iloc[i] == 1 and lower.iloc[i] < lower.iloc[i - 1]:
                lower.iloc[i] = lower.iloc[i - 1]
            if direction.iloc[i] == -1 and upper.iloc[i] > upper.iloc[i - 1]:
                upper.iloc[i] = upper.iloc[i - 1]
        st.iloc[i] = lower.iloc[i] if direction.iloc[i] == 1 else upper.iloc[i]
    return st


# ──────────────────────────────────────────────────────────────────────────────
# 1. NanosecondLiquidity
# ──────────────────────────────────────────────────────────────────────────────

class NanosecondLiquidity(Strategy):
    """
    Mean-reversion on bid/ask spread proxy + order-book imbalance proxy.
    Enters when spread is wide and price deviates from a fast EMA.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.ema_period   = self.params.get("ema_period",   5)
        self.threshold    = self.params.get("threshold",    0.0005)
        self.sl_pct       = self.params.get("sl_pct",       0.0005)
        self.tp_pct       = self.params.get("tp_pct",       0.001)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        close, high, low = df["close"], df["high"], df["low"]

        fair = ema(close, self.ema_period)

        denom = (high - low).replace(0, np.nan)
        spread_pct = (high - low) / close
        avg_spread = spread_pct.rolling(20).mean()

        # order-book imbalance proxy  (0 = fully at lows, 1 = fully at highs)
        obi = ((close - low) / denom).fillna(0.5)

        sig = pd.Series(0, index=df.index)

        wide = spread_pct > avg_spread * 1.2
        long_cond  = wide & (close < fair * (1 - self.threshold)) & (obi > 0.4)
        short_cond = wide & (close > fair * (1 + self.threshold)) & (obi < 0.6)

        sig[long_cond]  =  1
        sig[short_cond] = -1

        return pd.DataFrame({"signal": sig})


# ──────────────────────────────────────────────────────────────────────────────
# 2. NicheConcentration
# ──────────────────────────────────────────────────────────────────────────────

class NicheConcentration(Strategy):
    """
    EMA crossover breakout filtered by RSI > 50 and above-average volume.
    Short on breakdown below EMA with bearish MACD histogram divergence.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.ema_period   = self.params.get("ema_period",      20)
        self.rsi_period   = self.params.get("rsi_period",      14)
        self.vol_period   = self.params.get("vol_period",      10)
        self.vol_mult     = self.params.get("vol_multiplier",  1.5)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        close, vol = df["close"], df["volume"]

        ema_line  = ema(close, self.ema_period)
        rsi_line  = rsi(close, self.rsi_period)
        vol_avg   = sma(vol, self.vol_period)

        prev_close = close.shift(1)
        prev_ema   = ema_line.shift(1)

        long_breakout  = (close > ema_line) & (prev_close <= prev_ema)
        short_breakdown = (close < ema_line) & (prev_close >= prev_ema)
        vol_confirm    = vol > self.vol_mult * vol_avg

        # MACD histogram for short confirmation
        _, _, hist = macd(close)
        bearish_div = hist < hist.shift(1)

        sig = pd.Series(0, index=df.index)
        sig[long_breakout  & (rsi_line > 50) & vol_confirm]                = 1
        sig[short_breakdown & (rsi_line < 50) & bearish_div & vol_confirm]  = -1

        return pd.DataFrame({"signal": sig})


# ──────────────────────────────────────────────────────────────────────────────
# 3. CascadeWeighting
# ──────────────────────────────────────────────────────────────────────────────

class CascadeWeighting(Strategy):
    """
    Trend-following with ADX-gated cascade entries.
    Uses EMA for trend direction, RSI to avoid overbought/oversold extremes,
    volume confirmation, and a simple engulfing-candle trigger.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.ema_period   = self.params.get("ema_period",  20)
        self.rsi_period   = self.params.get("rsi_period",  14)
        self.adx_period   = self.params.get("adx_period",  14)
        self.atr_period   = self.params.get("atr_period",  14)
        self.vol_period   = self.params.get("vol_period",  10)
        self.vol_mult     = self.params.get("vol_mult",    1.5)
        self.adx_thresh   = self.params.get("adx_thresh",  25)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        close  = df["close"]
        high   = df["high"]
        low    = df["low"]
        volume = df["volume"]

        ema_line = ema(close, self.ema_period)
        rsi_line = rsi(close, self.rsi_period)
        vol_avg  = sma(volume, self.vol_period)

        # ADX approximation via smoothed true-range directional movement
        tr   = pd.concat([high - low,
                          (high - close.shift()).abs(),
                          (low  - close.shift()).abs()], axis=1).max(axis=1)
        adx_proxy = tr.rolling(self.adx_period).mean()   # simplified ATR as ADX proxy

        # Engulfing candle
        o, c = df["open"], close
        bull_eng = (c.shift(1) < o.shift(1)) & (o <= c.shift(1)) & (c >= o.shift(1)) & (c > o)
        bear_eng = (c.shift(1) > o.shift(1)) & (o >= c.shift(1)) & (c <= o.shift(1)) & (c < o)

        uptrend   = close > ema_line
        downtrend = close < ema_line
        vol_ok    = volume > self.vol_mult * vol_avg
        trend_strong = adx_proxy > adx_proxy.rolling(self.adx_period).mean()

        sig = pd.Series(0, index=df.index)
        sig[uptrend   & bull_eng & (rsi_line < 70) & vol_ok & trend_strong] =  1
        sig[downtrend & bear_eng & (rsi_line > 30) & vol_ok & trend_strong] = -1

        return pd.DataFrame({"signal": sig})


# ──────────────────────────────────────────────────────────────────────────────
# 4. SynergisticConfluence
# ──────────────────────────────────────────────────────────────────────────────

class SynergisticConfluence(Strategy):
    """
    Requires ≥ 3 of 6 signals to align before entering.
    Signals: dual-EMA trend, Fib retracement zone, MACD direction,
             RSI extreme bounce, volume surge, SuperTrend direction.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.ema_fast_p      = self.params.get("ema_fast",   50)
        self.ema_slow_p      = self.params.get("ema_slow",   200)
        self.rsi_period      = self.params.get("rsi_period", 14)
        self.atr_period      = self.params.get("atr_period", 14)
        self.vol_period      = self.params.get("vol_period", 20)
        self.threshold       = self.params.get("threshold",  3)
        self.st_mult         = self.params.get("st_mult",    3.0)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        close  = df["close"]
        high   = df["high"]
        low    = df["low"]
        volume = df["volume"]

        ema_f = ema(close, self.ema_fast_p)
        ema_s = ema(close, self.ema_slow_p)
        rsi_l = rsi(close, self.rsi_period)
        atr_l = atr(high, low, close, self.atr_period)
        vol_a = sma(volume, self.vol_period)
        _, _, hist = macd(close)

        # SuperTrend
        st = _supertrend(high, low, close, atr_l, self.st_mult)

        # Fib zones from rolling 20-bar swing
        swing_h = high.rolling(20).max().shift(1)
        swing_l = low.rolling(20).min().shift(1)
        fib_rng = (swing_h - swing_l).replace(0, np.nan)
        fib_382 = swing_h - 0.382 * fib_rng
        fib_618 = swing_h - 0.618 * fib_rng

        # Long score
        l1 = ((ema_f > ema_s) & (close > ema_f)).astype(int)
        l2 = (close <= fib_382).astype(int)
        l3 = ((hist > 0) & (hist > hist.shift(1))).astype(int)
        l4 = ((rsi_l < 40) & (rsi_l > rsi_l.shift(1))).astype(int)
        l5 = (volume > vol_a * 1.2).astype(int)
        l6 = (close > st).astype(int)
        long_score = l1 + l2 + l3 + l4 + l5 + l6

        # Short score
        s1 = ((ema_f < ema_s) & (close < ema_f)).astype(int)
        s2 = (close >= fib_618).astype(int)
        s3 = ((hist < 0) & (hist < hist.shift(1))).astype(int)
        s4 = ((rsi_l > 60) & (rsi_l < rsi_l.shift(1))).astype(int)
        s5 = l5
        s6 = (close < st).astype(int)
        short_score = s1 + s2 + s3 + s4 + s5 + s6

        sig = pd.Series(0, index=df.index)
        sig[long_score  >= self.threshold] =  1
        sig[short_score >= self.threshold] = -1

        return pd.DataFrame({"signal": sig})


# ──────────────────────────────────────────────────────────────────────────────
# 5. KalmanSentiment
# ──────────────────────────────────────────────────────────────────────────────

class KalmanSentiment(Strategy):
    """
    Kalman-filtered pct-change velocity as a sentiment proxy.
    Long when velocity is rising and price is above VWAP-proxy; short when falling.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.rsi_period  = self.params.get("rsi_period", 14)
        self.vel_period  = self.params.get("vel_period", 30)
        self.kalman_q    = self.params.get("kalman_q",   0.01)
        self.kalman_r    = self.params.get("kalman_r",   0.05)
        self.vel_mult    = self.params.get("vel_mult",   2.0)
        self.rsi_ob      = self.params.get("rsi_ob",     70)
        self.rsi_os      = self.params.get("rsi_os",     30)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        close  = df["close"]
        volume = df["volume"]

        # Proxy rate (pct change)
        pr = close.pct_change().fillna(0).values
        filtered = _kalman(pr, self.kalman_q, self.kalman_r)
        velocity = np.concatenate(([0.0], np.diff(filtered)))

        vel_s  = pd.Series(velocity, index=df.index)
        vel_std = vel_s.rolling(self.vel_period).std().fillna(0)
        dyn_thr = vel_std * self.vel_mult

        # VWAP proxy: cumulative (typical * vol) / cumulative vol, reset daily
        typical = (df["high"] + df["low"] + close) / 3
        pv      = typical * volume
        # daily reset approximation using rolling 390-bar window (≈ 1 trading day of 1m bars)
        vwap_proxy = pv.rolling(min(390, len(df))).sum() / volume.rolling(min(390, len(df))).sum()

        rsi_l = rsi(close, self.rsi_period)
        filt_s = pd.Series(filtered, index=df.index)

        long_cond  = (vel_s > dyn_thr)  & (filt_s > 0) & (rsi_l < self.rsi_ob) & (close > vwap_proxy)
        short_cond = (vel_s < -dyn_thr) & (filt_s < 0) & (rsi_l > self.rsi_os) & (close < vwap_proxy)

        sig = pd.Series(0, index=df.index)
        sig[long_cond]  =  1
        sig[short_cond] = -1

        return pd.DataFrame({"signal": sig})


# ──────────────────────────────────────────────────────────────────────────────
# 6. KellyFractional
# ──────────────────────────────────────────────────────────────────────────────

class KellyFractional(Strategy):
    """
    Kelly criterion position sizing with periodic rebalancing.
    Long only: allocates Kelly-fraction of equity to the market,
    goes flat when Kelly fraction ≤ 0.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.window        = self.params.get("window",       252)
        self.kelly_factor  = self.params.get("kelly_factor", 0.5)
        self.rebal_period  = self.params.get("rebal_period", 30)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        close = df["close"]
        returns = close.pct_change()

        mu  = returns.rolling(self.window).mean()
        s2  = returns.rolling(self.window).var()

        raw_kelly = (self.kelly_factor * (mu / s2.replace(0, np.nan))).clip(0, 1).fillna(0)

        # Resample to rebalancing grid: carry signal forward
        sig = pd.Series(0, index=df.index)
        last_signal = 0
        for i, (idx, kf) in enumerate(raw_kelly.items()):
            if i % self.rebal_period == 0:
                last_signal = 1 if kf > 0 else 0
            sig[idx] = last_signal

        return pd.DataFrame({"signal": sig})


# ──────────────────────────────────────────────────────────────────────────────
# 7. BullishSqueeze
# ──────────────────────────────────────────────────────────────────────────────

class BullishSqueeze(Strategy):
    """
    Bollinger Band squeeze breakout (long only).
    Enters when BBW is at a 20-bar minimum and price is above SMA-200.
    Exits when BBW expands back above its 10-bar average.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.bb_period   = self.params.get("bb_period",  20)
        self.bb_std      = self.params.get("bb_std",     2.0)
        self.sma_long    = self.params.get("sma_long",   200)
        self.bbw_min_p   = self.params.get("bbw_min_p",  20)
        self.bbw_sma_p   = self.params.get("bbw_sma_p",  10)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        close = df["close"]

        upper, middle, lower = bollinger_bands(close, self.bb_period, self.bb_std)
        bbw      = upper - lower
        bbw_min  = bbw.rolling(self.bbw_min_p).min()
        bbw_avg  = bbw.rolling(self.bbw_sma_p).mean()
        sma200   = sma(close, self.sma_long)

        squeeze    = bbw <= bbw_min
        trend_up   = close > sma200
        in_squeeze = squeeze & trend_up

        # Signal: enter on squeeze, exit when BBW expands
        sig = pd.Series(0, index=df.index)
        position = False
        for i in range(len(df)):
            if position:
                if bbw.iloc[i] > bbw_avg.iloc[i]:
                    position = False
                else:
                    sig.iloc[i] = 1
            else:
                if in_squeeze.iloc[i]:
                    position = True
                    sig.iloc[i] = 1

        return pd.DataFrame({"signal": sig})


# ──────────────────────────────────────────────────────────────────────────────
# 8. EarningsPrelude
# ──────────────────────────────────────────────────────────────────────────────

class EarningsPrelude(Strategy):
    """
    Momentum entry on SMA breakout + RSI > 50 + volume surge + bullish candle.
    Exits on SMA break. Long only.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.sma_period  = self.params.get("sma_period",  20)
        self.rsi_period  = self.params.get("rsi_period",  14)
        self.vol_period  = self.params.get("vol_period",  10)
        self.vol_mult    = self.params.get("vol_mult",    1.5)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        close  = df["close"]
        open_  = df["open"]
        volume = df["volume"]

        sma_line = sma(close, self.sma_period)
        rsi_line = rsi(close, self.rsi_period)
        vol_avg  = sma(volume, self.vol_period)

        bullish_candle = close > open_
        vol_spike      = volume > self.vol_mult * vol_avg
        above_sma      = close > sma_line

        entry = above_sma & (rsi_line > 50) & vol_spike & bullish_candle
        exit_ = close < sma_line

        sig = pd.Series(0, index=df.index)
        position = False
        for i in range(len(df)):
            if position:
                if exit_.iloc[i]:
                    position = False
                else:
                    sig.iloc[i] = 1
            else:
                if entry.iloc[i]:
                    position = True
                    sig.iloc[i] = 1

        return pd.DataFrame({"signal": sig})
