"""
Statistical arbitrage strategies using single-instrument price series.

  ZScoreMeanReversion   — trade z-score of price vs rolling mean
  HalfLifeMeanReversion — Ornstein-Uhlenbeck half-life-scaled reversion
  AutocorrMomentum      — exploit serial autocorrelation in returns
  RollingBetaNeutral    — hedge-ratio-scaled long/short on rolling beta residual
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import sma, ema


class ZScoreMeanReversion(Strategy):
    """
    Z-score of close vs rolling mean. Long when z < -threshold, short when z > threshold.
    Exit when z reverts toward zero.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.window    = self.params.get("window",    30)
        self.threshold = self.params.get("threshold",  2.0)
        self.exit_z    = self.params.get("exit_z",     0.5)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c = df["close"]

        roll_mean = c.rolling(self.window).mean()
        roll_std  = c.rolling(self.window).std().replace(0, np.nan)
        z_score   = (c - roll_mean) / roll_std

        sig = pd.Series(0, index=df.index)
        in_pos = 0
        for i in range(len(df)):
            z = z_score.iloc[i]
            if pd.isna(z):
                continue
            if in_pos == 1:
                if z >= -self.exit_z:
                    in_pos = 0
                else:
                    sig.iloc[i] = 1
            elif in_pos == -1:
                if z <= self.exit_z:
                    in_pos = 0
                else:
                    sig.iloc[i] = -1
            else:
                if z < -self.threshold:
                    in_pos = 1
                    sig.iloc[i] = 1
                elif z > self.threshold:
                    in_pos = -1
                    sig.iloc[i] = -1
        return pd.DataFrame({"signal": sig})


class HalfLifeMeanReversion(Strategy):
    """
    Estimates Ornstein-Uhlenbeck half-life via OLS on lagged returns.
    Uses the half-life to scale the lookback window for mean reversion.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.min_hl    = self.params.get("min_halflife",  5)
        self.max_hl    = self.params.get("max_halflife", 60)
        self.est_win   = self.params.get("estimation_window", 120)
        self.z_thresh  = self.params.get("z_threshold", 1.5)

    def _halflife(self, series: pd.Series) -> float:
        lag  = series.shift(1).dropna()
        delta = series.diff().dropna()
        lag, delta = lag.align(delta, join="inner")
        if len(lag) < 10:
            return self.min_hl
        try:
            beta = np.polyfit(lag.values, delta.values, 1)[0]
            if beta >= 0:
                return self.max_hl
            hl = -np.log(2) / beta
            return float(np.clip(hl, self.min_hl, self.max_hl))
        except Exception:
            return self.min_hl

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c = df["close"]
        sig = pd.Series(0, index=df.index)

        for i in range(self.est_win, len(df)):
            window = c.iloc[i - self.est_win: i]
            hl     = self._halflife(window)
            w      = max(int(round(hl)), self.min_hl)
            mu     = c.iloc[i - w: i].mean()
            sd     = c.iloc[i - w: i].std()
            if sd == 0 or pd.isna(sd):
                continue
            z = (c.iloc[i] - mu) / sd
            if z < -self.z_thresh:
                sig.iloc[i] = 1
            elif z > self.z_thresh:
                sig.iloc[i] = -1

        return pd.DataFrame({"signal": sig})


class AutocorrMomentum(Strategy):
    """
    Exploits positive serial autocorrelation.
    If rolling return autocorrelation > threshold, follow the trend.
    If negative, fade it (mean revert).
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.lag       = self.params.get("lag",       1)
        self.window    = self.params.get("window",   20)
        self.ac_thresh = self.params.get("ac_thresh", 0.1)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c = df["close"]
        rets = c.pct_change()

        def rolling_ac(series: pd.Series, lag: int, win: int) -> pd.Series:
            result = pd.Series(np.nan, index=series.index)
            for i in range(win + lag - 1, len(series)):
                s = series.iloc[i - win - lag + 1: i + 1]
                if s.std() == 0:
                    continue
                result.iloc[i] = s.autocorr(lag=lag)
            return result

        ac = rolling_ac(rets, self.lag, self.window)
        last_ret = rets.shift(self.lag)

        sig = pd.Series(0, index=df.index)
        # Positive AC → momentum; negative AC → mean reversion
        sig[(ac >  self.ac_thresh) & (last_ret > 0)] =  1
        sig[(ac >  self.ac_thresh) & (last_ret < 0)] = -1
        sig[(ac < -self.ac_thresh) & (last_ret > 0)] = -1
        sig[(ac < -self.ac_thresh) & (last_ret < 0)] =  1
        return pd.DataFrame({"signal": sig})


class RollingBetaNeutral(Strategy):
    """
    Estimates beta of close vs its own rolling EMA trend,
    then trades deviations (residuals) from that trend.
    Long when residual is negative (below fair); short when positive.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.trend_p  = self.params.get("trend_period", 50)
        self.resid_p  = self.params.get("resid_period", 20)
        self.z_thresh = self.params.get("z_threshold",  1.5)

    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        c = df["close"]

        trend    = ema(c, self.trend_p)
        residual = c - trend
        mu_r     = residual.rolling(self.resid_p).mean()
        sd_r     = residual.rolling(self.resid_p).std().replace(0, np.nan)
        z        = (residual - mu_r) / sd_r

        sig = pd.Series(0, index=df.index)
        sig[z < -self.z_thresh] =  1
        sig[z >  self.z_thresh] = -1
        return pd.DataFrame({"signal": sig})
