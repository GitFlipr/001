"""Long Nov–Apr, flat May–Oct. From set_2/073."""
import pandas as pd
from backtesting import Strategy


class SellInMay(Strategy):
    def init(self):
        pass
    def next(self):
        if len(self.data) < 80:
            return
        m = (
            self.data.index[-1].month
            if hasattr(self.data.index[-1], "month")
            else pd.Timestamp(self.data.index[-1]).month
        )
        winter = m in (11, 12, 1, 2, 3, 4)
        if winter and not self.position:
            self.buy()
        elif not winter and self.position:
            self.position.close()
