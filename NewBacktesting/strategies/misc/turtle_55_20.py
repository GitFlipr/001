"""Classic Turtle Trading: 55-day breakout entry, 20-day exit (Donchian)."""

import talib
from backtesting import Strategy


class Turtle55_20(Strategy):
    entry_n = 55
    exit_n = 20

    def init(self):
        self.entry_up = self.I(talib.MAX, self.data.High, timeperiod=self.entry_n)
        self.entry_dn = self.I(talib.MIN, self.data.Low, timeperiod=self.entry_n)
        self.exit_up = self.I(talib.MAX, self.data.High, timeperiod=self.exit_n)
        self.exit_dn = self.I(talib.MIN, self.data.Low, timeperiod=self.exit_n)

    def next(self):
        if len(self.data) < max(self.entry_n, self.exit_n) + 3:
            return

        c = self.data.Close[-1]
        up = c > self.entry_up[-2]
        dn = c < self.entry_dn[-2]

        if not self.position:
            if up:
                self.buy()
            elif dn:
                self.sell()
        else:
            if self.position.is_long and c < self.exit_dn[-2]:
                self.position.close()
            elif self.position.is_short and c > self.exit_up[-2]:
                self.position.close()

