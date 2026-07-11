"""Gap trading: go with gap direction when gap > threshold. From set_2/095 (Strats21)."""
from backtesting import Strategy


class Strats21GapTrading(Strategy):
    gap_pct = 0.01

    def init(self):
        pass

    def next(self):
        if len(self.data) < 2:
            return
        prev_c = self.data.Close[-2]
        o = self.data.Open[-1]
        if prev_c <= 0:
            return
        g = (o - prev_c) / prev_c
        if not self.position:
            if g > self.gap_pct:
                self.buy()
            elif g < -self.gap_pct:
                self.sell()
        else:
            if self.position.is_long and self.data.Close[-1] < o:
                self.position.close()
            elif self.position.is_short and self.data.Close[-1] > o:
                self.position.close()
