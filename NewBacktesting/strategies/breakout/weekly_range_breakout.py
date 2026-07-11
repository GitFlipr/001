"""Weekly range breakout: Monday's range sets the week; trade break of Mon high/low."""
import pandas as pd
import talib
from backtesting import Strategy


class WeeklyRangeBreakout(Strategy):
    """Uses weekly aggregation: break of prior week's high/low."""

    def init(self):
        # Use rolling 5-day (approx week) high/low on daily data
        self.wk_high = self.I(talib.MAX, self.data.High, timeperiod=5)
        self.wk_low = self.I(talib.MIN, self.data.Low, timeperiod=5)

    def next(self):
        if len(self.data) < 8:
            return
        ts = self.data.index[-1]
        dow = ts.dayofweek if hasattr(ts, "dayofweek") else pd.Timestamp(ts).dayofweek
        c = self.data.Close[-1]

        # Use prior "week" (5 bars) high/low
        hi, lo = self.wk_high[-6], self.wk_low[-6]

        if not self.position:
            if c > hi:
                self.buy()
            elif c < lo:
                self.sell()
        else:
            if self.position.is_long and c < self.wk_low[-2]:
                self.position.close()
            elif self.position.is_short and c > self.wk_high[-2]:
                self.position.close()
