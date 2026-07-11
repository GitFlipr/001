"""Bullish/bearish engulfing; hammer/hanging-man. From set_1/022."""
from backtesting import Strategy


class EngulfingReversal(Strategy):
    body_ratio_hammer = 0.35

    def init(self):
        pass

    def next(self):
        if len(self.data) < 3:
            return
        o, h, l, c = self.data.Open[-1], self.data.High[-1], self.data.Low[-1], self.data.Close[-1]
        po, ph, pl, pc = self.data.Open[-2], self.data.High[-2], self.data.Low[-2], self.data.Close[-2]
        rng = max(h - l, 1e-12)
        body = abs(c - o)
        prev_body = abs(pc - po)
        bull_engulf = pc < po and c > o and c >= po and o <= pc and c - o > prev_body
        bear_engulf = pc > po and c < o and o >= pc and c <= po and o - c > prev_body
        lower_wick = min(o, c) - l
        upper_wick = h - max(o, c)
        hammer = body / rng < self.body_ratio_hammer and lower_wick > 2 * body and upper_wick < body
        hanging = hammer and c > o

        if not self.position:
            if bull_engulf or hammer:
                self.buy()
            elif bear_engulf or hanging:
                self.sell()
        else:
            if self.position.is_long and (bear_engulf or hanging):
                self.position.close()
            elif self.position.is_short and (bull_engulf or hammer):
                self.position.close()
