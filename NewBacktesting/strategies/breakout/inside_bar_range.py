"""Inside Bar Range - Active strategy (Neutral). Backtesting adapter."""
import sys
from pathlib import Path
import pandas as pd
from backtesting import Strategy

_ALLREGIME = Path(__file__).resolve().parents[4] / "New_Dev" / "AllRegime_Master_Bot"
if _ALLREGIME.exists() and str(_ALLREGIME) not in sys.path:
    sys.path.insert(0, str(_ALLREGIME))

_detect = None
try:
    from shared.candlestick_patterns import detect_inside_bar
    _detect = detect_inside_bar
except ImportError:
    pass


def _inside_bar_signal(df: pd.DataFrame) -> bool:
    if _detect:
        return _detect(df)
    if df is None or len(df) < 2:
        return False
    prev = df.iloc[-2]
    curr = df.iloc[-1]
    ph, pl = prev["High"], prev["Low"]
    ch, cl = curr["High"], curr["Low"]
    return ch < ph and cl > pl


class InsideBarRangeStrategy(Strategy):
    """Inside bar in range - consolidation breakout (Neutral)."""

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
        if _inside_bar_signal(df) and not self.position:
            self.buy()
