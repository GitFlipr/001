"""
Calendar seasonality strategy migrated from the legacy backup set.
"""
import pandas as pd

from backtest.strategies.base import Strategy


class CalendarSeasonality(Strategy):
    """
    Enter long around month-end / early month and exit mid-month.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["signal"] = 0
        for idx, ts in enumerate(df.index):
            if hasattr(ts, "day"):
                dom = ts.day
            else:
                dom = pd.Timestamp(ts).day
            if dom >= 25 or dom <= 3:
                df.at[ts, "signal"] = 1
            elif 10 <= dom <= 20:
                df.at[ts, "signal"] = 0
        return df[["signal"]]
