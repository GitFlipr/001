"""Tue drawdown vs Mon range → long on Wed. From set_2/058."""
import pandas as pd
from backtesting import Strategy


class MtwGapReversal(Strategy):
    gap_threshold = 0.03

    def init(self):
        pass

    def next(self):
        if len(self.data) < 4:
            return
        ts = self.data.index[-1]
        dow = ts.dayofweek if hasattr(ts, "dayofweek") else pd.Timestamp(ts).dayofweek
        if self.position and dow == 3:
            self.position.close()
            return
        if dow != 2:
            return
        mon_c = float(self.data.Close[-3])
        tue_l = float(self.data.Low[-2])
        if mon_c <= 0:
            return
        stress = (mon_c - tue_l) / mon_c
        if not self.position and stress >= self.gap_threshold:
            self.buy()
