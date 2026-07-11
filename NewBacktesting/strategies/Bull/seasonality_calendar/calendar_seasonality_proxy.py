"""Month-turn seasonality proxy (calendar trading). From set_1/021."""
from backtesting import Strategy
import pandas as pd


class CalendarSeasonalityProxy(Strategy):
    """Long into month-end / first session of month."""

    def init(self):
        pass
    def next(self):
        if len(self.data) < 80:
            return
        ts = self.data.index[-1]
        if hasattr(ts, "day"):
            dom = ts.day
        else:
            t = pd.Timestamp(ts)
            dom = t.day
        if not self.position:
            if dom >= 25 or dom <= 3:
                self.buy()
        else:
            if self.position.is_long and 10 <= dom <= 20:
                self.position.close()
