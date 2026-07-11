"""
Window Oscillators Multi-Timeframe - From 119.
Stochastic/RSI across timeframes. Oversold on short + bullish on long = buy.
Uses single timeframe with different periods as proxy for MTF.
"""
import numpy as np
from backtesting import Strategy
import talib


class WindowOscillatorsMTFStrategy(Strategy):
    """
    Proxy for MTF: short-period RSI (oversold/overbought) + long-period RSI (trend).
    Buy: short RSI < 30 (oversold) and long RSI > 50 (bullish).
    Sell: short RSI > 70 (overbought) and long RSI < 50 (bearish).
    """

    short_period = 7
    long_period = 21

    def init(self):
        close = self.data.Close
        high = self.data.High
        low = self.data.Low
        self.rsi_short = self.I(talib.RSI, close, timeperiod=self.short_period)
        self.rsi_long = self.I(talib.RSI, close, timeperiod=self.long_period)
        self.stoch_k, self.stoch_d = self.I(talib.STOCH, high, low, close, 14, 3, 0, 3, 0)

    def next(self):
        if len(self.data) < self.long_period + 5:
            return
        if np.isnan(self.rsi_long[-1]) or np.isnan(self.stoch_k[-1]):
            return

        rsi_s = self.rsi_short[-1]
        rsi_l = self.rsi_long[-1]
        stoch = self.stoch_k[-1]

        oversold_short = rsi_s < 30 or stoch < 20
        overbought_short = rsi_s > 70 or stoch > 80
        bullish_long = rsi_l > 50
        bearish_long = rsi_l < 50

        if not self.position:
            if oversold_short and bullish_long:
                self.buy()
            elif overbought_short and bearish_long:
                self.sell()
        else:
            if self.position.is_long and (overbought_short or bearish_long):
                self.position.close()
            elif self.position.is_short and (oversold_short or bullish_long):
                self.position.close()
