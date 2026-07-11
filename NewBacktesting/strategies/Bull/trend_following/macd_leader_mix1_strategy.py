import pandas as pd
import numpy as np
import talib
from backtesting import Strategy
from backtesting.lib import crossover


class MACDLeaderMix1(Strategy):
    ema_period = 50
    macd_fast = 11
    macd_slow = 24
    macd_signal = 7
    swing_lookback = 20
    rr_ratio = 3.0
    cooldown_bars = 24
    max_hold_bars = 240

    def init(self):
        super().init()
        close = self.data.Close
        self.mix1_line = self.I(talib.EMA, close, self.ema_period)
        self.macd_line, self.macd_signal_line, self.macd_hist = self.I(
            talib.MACD, close,
            fastperiod=self.macd_fast,
            slowperiod=self.macd_slow,
            signalperiod=self.macd_signal
        )
        self.last_trade_exit_bar = -np.inf
        self.entry_bar = None

    def on_trade(self, trade):
        # Called when a trade is opened or closed
        if trade.is_closed:
            # Record that the trade closed at this bar
            self.last_trade_exit_bar = len(self.data)
            self.entry_bar = None

    def next(self):
        # If a position is open for too long, close it
        if self.position and self.entry_bar is not None:
            if len(self.data) - self.entry_bar > self.max_hold_bars:
                self.position.close()
                return  # on_trade will handle resetting last_trade_exit_bar and entry_bar

        # Only consider new entries if no position and cooldown has passed
        if not self.position and len(self.data) - self.last_trade_exit_bar > self.cooldown_bars:
            close = self.data.Close[-1]
            open_ = self.data.Open[-1]
            macd_line = self.macd_line[-1]
            macd_signal_line = self.macd_signal_line[-1]
            mix1_line = self.mix1_line[-1]

            is_green = close > open_
            price_above_mix1_strong = close > mix1_line * 1.002
            strong_bull_macd = macd_line > macd_signal_line and macd_line > 0.001

            is_red = close < open_
            price_below_mix1_strong = close < mix1_line * 0.998
            strong_bear_macd = macd_line < macd_signal_line and macd_line < -0.001

            recent_closes = self.data.Close[-self.swing_lookback-1:-1]
            recent_high = recent_closes.max() if len(recent_closes) > 0 else close
            recent_low = recent_closes.min() if len(recent_closes) > 0 else close

            # Long setup
            if is_green and price_above_mix1_strong and strong_bull_macd:
                stop_loss = min(recent_low, mix1_line)
                if stop_loss < close:
                    risk = close - stop_loss
                    tp = close + risk * self.rr_ratio
                    self.buy(sl=stop_loss, tp=tp)
                    self.entry_bar = len(self.data)

            # Short setup
            elif is_red and price_below_mix1_strong and strong_bear_macd:
                stop_loss = max(recent_high, mix1_line)
                if stop_loss > close:
                    risk = stop_loss - close
                    tp = close - risk * self.rr_ratio
                    self.sell(sl=stop_loss, tp=tp)
                    self.entry_bar = len(self.data)
