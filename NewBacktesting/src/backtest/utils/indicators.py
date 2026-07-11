"""
Technical Indicators
"""
import pandas as pd
import numpy as np


def sma(series: pd.Series, period: int) -> pd.Series:
    """Simple Moving Average"""
    return series.rolling(window=period).mean()


def ema(series: pd.Series, period: int) -> pd.Series:
    """Exponential Moving Average"""
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """Relative Strength Index"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0.0))
    loss = (-delta.where(delta < 0, 0.0))
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    rs = avg_gain / (avg_loss + 1e-10)  # Avoid division by zero
    return 100 - (100 / (1 + rs))


def crossover(series1: pd.Series, series2: pd.Series) -> pd.Series:
    """Returns 1 where series1 crosses above series2, -1 where it crosses below"""
    cross_up = ((series1 > series2) & (series1.shift(1) <= series2.shift(1)))
    cross_down = ((series1 < series2) & (series1.shift(1) >= series2.shift(1)))
    return cross_up.astype(int) - cross_down.astype(int)


def bollinger_bands(series: pd.Series, period: int = 20, num_std: float = 2.0) -> tuple[pd.Series, pd.Series, pd.Series]:
    """Returns upper band, middle band (SMA), lower band"""
    sma_series = sma(series, period)
    std = series.rolling(window=period).std()
    upper = sma_series + (std * num_std)
    lower = sma_series - (std * num_std)
    return upper, sma_series, lower


def macd(
    series: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> tuple[pd.Series, pd.Series, pd.Series]:
    """MACD line, signal line, histogram"""
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    histogram = macd_line - signal_line
    return macd_line, signal_line, histogram


def atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """Average True Range"""
    high = data["high"]
    low = data["low"]
    close = data["close"].shift(1)
    tr1 = high - low
    tr2 = abs(high - close)
    tr3 = abs(low - close)
    true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return true_range.rolling(window=period).mean()


def roc(series: pd.Series, period: int = 10) -> pd.Series:
    """Rate of Change"""
    return ((series - series.shift(period)) / (series.shift(period) + 1e-10)) * 100


def stoch_rsi(data: pd.Series, rsi_period=14, stoch_period=14, smooth_k=3, smooth_d=3) -> tuple[pd.Series, pd.Series]:
    """Stochastic RSI: returns K and D"""
    rsi_series = rsi(data, rsi_period)
    min_rsi = rsi_series.rolling(stoch_period).min()
    max_rsi = rsi_series.rolling(stoch_period).max()
    stoch_rsi = (rsi_series - min_rsi) / (max_rsi - min_rsi + 1e-10)
    k = sma(stoch_rsi, smooth_k) * 100
    d = sma(k, smooth_d)
    return k, d
