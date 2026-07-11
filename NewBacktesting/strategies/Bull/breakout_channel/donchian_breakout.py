"""
Classic breakout channel (Turtle-style simplification): enter on N-bar high/low break.
Trend-following, can whipsaw in ranges — combine with volatility filter in research.

Not financial advice.
"""
from backtesting import Strategy


class DonchianBreakoutStrategy(Strategy):
    entry_bars = 20
    exit_bars = 10

    def init(self):
        pass

    def next(self):
        n, m = self.entry_bars, self.exit_bars
        if len(self.data) < n + 2:
            return
        h, l = self.data.High, self.data.Low
        c = self.data.Close[-1]
        entry_high = max(float(h[i]) for i in range(-n - 1, -1))
        entry_low = min(float(l[i]) for i in range(-n - 1, -1))
        exit_high = max(float(h[i]) for i in range(-m - 1, -1)) if len(self.data) > m + 1 else entry_high
        exit_low = min(float(l[i]) for i in range(-m - 1, -1)) if len(self.data) > m + 1 else entry_low

        if not self.position:
            if c > entry_high:
                self.buy()
            elif c < entry_low:
                self.sell()
        else:
            if self.position.is_long and c < exit_low:
                self.position.close()
            elif self.position.is_short and c > exit_high:
                self.position.close()
