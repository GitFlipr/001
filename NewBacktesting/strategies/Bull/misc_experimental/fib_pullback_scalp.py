"""Fib pullback scalper using rolling swing high/low (TA-Lib).

Idea:
- Define swing range as highest high / lowest low over lookback (no lookahead: use previous bar).
- Trade with trend (EMA) on pullback to a fib level and scalp back toward 0.382/0.5.
"""

import numpy as np
import talib
from backtesting import Strategy


class FibPullbackScalp(Strategy):
    lookback = 60
    trend_ema = 100

    fib_entry = 0.618
    fib_take = 0.382

    atr_period = 14
    stop_atr_mult = 1.8

    def init(self):
        h = self.data.High
        l = self.data.Low
        c = self.data.Close
        self.hh = self.I(talib.MAX, h, timeperiod=self.lookback)
        self.ll = self.I(talib.MIN, l, timeperiod=self.lookback)
        self.ema = self.I(talib.EMA, c, timeperiod=self.trend_ema)
        self.atr = self.I(talib.ATR, h, l, c, timeperiod=self.atr_period)

    def next(self):
        need = max(self.lookback, self.trend_ema, self.atr_period) + 5
        if len(self.data) < need:
            return
        c = float(self.data.Close[-1])
        ema = float(self.ema[-1])
        atr = float(self.atr[-1])
        if any(np.isnan(x) for x in (ema, atr)) or atr <= 0:
            return

        # Use prior bar swing range to avoid same-bar lookahead.
        hh = float(self.hh[-2])
        ll = float(self.ll[-2])
        if any(np.isnan(x) for x in (hh, ll)) or hh <= ll:
            return

        rng = hh - ll

        uptrend = c >= ema
        dntrend = c <= ema

        if uptrend:
            entry_level = hh - self.fib_entry * rng
            take_level = hh - self.fib_take * rng
            if not self.position and c <= entry_level:
                sl = c - self.stop_atr_mult * atr
                if sl < c:
                    self.buy(sl=sl)
            elif self.position and self.position.is_long and c >= take_level:
                self.position.close()
        elif dntrend:
            entry_level = ll + self.fib_entry * rng
            take_level = ll + self.fib_take * rng
            if not self.position and c >= entry_level:
                sl = c + self.stop_atr_mult * atr
                if c < sl:
                    self.sell(sl=sl)
            elif self.position and self.position.is_short and c <= take_level:
                self.position.close()

