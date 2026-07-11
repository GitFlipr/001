from backtesting import Strategy
import numpy as np
import talib


class TrendFollowingStrategy(Strategy):
    """Adaptive trend following strategy combining multiple indicators."""

    fast_ma_period = 50
    slow_ma_period = 200
    adx_period = 14
    atr_period = 14
    rsi_period = 14
    atr_stop_multiplier = 2.0

    def init(self):
        self.fast_ma = self.I(talib.EMA, self.data.Close, timeperiod=self.fast_ma_period)
        self.slow_ma = self.I(talib.EMA, self.data.Close, timeperiod=self.slow_ma_period)
        self.adx = self.I(
            talib.ADX,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.adx_period,
        )
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.atr = self.I(
            talib.ATR,
            self.data.High,
            self.data.Low,
            self.data.Close,
            timeperiod=self.atr_period,
        )

    def next(self):
        if len(self.data) < self.slow_ma_period:
            return

        price = float(self.data.Close[-1])
        atr = float(self.atr[-1]) if not np.isnan(self.atr[-1]) else 0.0
        if atr <= 0:
            return

        stop_distance = atr * self.atr_stop_multiplier
        fast = float(self.fast_ma[-1])
        slow = float(self.slow_ma[-1])
        rsi = float(self.rsi[-1])
        adx = float(self.adx[-1])
        strong_trend = adx > 25

        if not self.position:
            if fast > slow and rsi > 50 and strong_trend:
                self.buy(sl=price - stop_distance, tp=price + (stop_distance * 2))
            elif fast < slow and rsi < 50 and strong_trend:
                self.sell(sl=price + stop_distance, tp=price - (stop_distance * 2))
        elif self.position.is_long:
            if fast < slow or rsi < 40:
                self.position.close()
        elif self.position.is_short:
            if fast > slow or rsi > 60:
                self.position.close()