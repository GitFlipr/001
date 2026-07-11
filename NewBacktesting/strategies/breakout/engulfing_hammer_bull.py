"""Engulfing Hammer Bull - Active strategy (Bull). Backtesting adapter."""
import sys
from pathlib import Path
import pandas as pd
from backtesting import Strategy

_ALLREGIME = Path(__file__).resolve().parents[4] / "New_Dev" / "AllRegime_Master_Bot"
if _ALLREGIME.exists() and str(_ALLREGIME) not in sys.path:
    sys.path.insert(0, str(_ALLREGIME))

_detect = None
try:
    from shared.candlestick_patterns import detect_bullish_engulfing_or_hammer
    _detect = detect_bullish_engulfing_or_hammer
except ImportError:
    pass


def _engulfing_hammer_signal(df: pd.DataFrame) -> bool:
    if _detect:
        return _detect(df)
    # Fallback: simple bullish engulfing
    if df is None or len(df) < 2:
        return False
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    po, pc = prev["Open"], prev["Close"]
    co, cc = curr["Open"], curr["Close"]
    if pc >= po or cc <= co:
        return False
    return co < pc and cc > po


class EngulfingHammerBullStrategy(Strategy):
    """Engulfing + Hammer (Bull) - candlestick reversal."""

    def init(self):
        pass

    def next(self):
        if len(self.data) < 2:
            return
        df = pd.DataFrame({
            "Open": self.data.Open, "High": self.data.High, "Low": self.data.Low,
            "Close": self.data.Close
        }, index=self.data.index)
        df = df.iloc[: len(self.data)]
        if _engulfing_hammer_signal(df) and not self.position:
            self.buy()
