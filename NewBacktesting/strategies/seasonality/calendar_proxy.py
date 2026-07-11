"""Calendar proxy: long mid-week, avoid Mon/Fri. From set_2/093 (Strats19)."""
import pandas as pd
from backtesting import Strategy


class Strats19CalendarProxy(Strategy):
    def init(self):
        pass
    def next(self):
        if len(self.data) < 80:
            return
        ts = self.data.index[-1]
        dow = ts.dayofweek if hasattr(ts, "dayofweek") else pd.Timestamp(ts).dayofweek
        if not self.position and dow in (1, 2, 3):
            self.buy()
        elif self.position and dow in (0, 4):
            self.position.close()
