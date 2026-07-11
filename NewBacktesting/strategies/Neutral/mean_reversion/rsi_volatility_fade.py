"""Range-bound mean reversion that fades overextended RSI moves when volatility cools."""
import talib
from backtesting import Strategy


class RSIVolatilityFade(Strategy):
    rsi_period = 14
    vol_period = 20
    entry_rsi = 70
    exit_rsi = 55

    def init(self):
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.vol_period)

    def next(self):
        if len(self.data) < self.vol_period + 2:
            return

        if not self.position:
            if self.rsi[-1] > self.entry_rsi and self.atr[-1] < self.atr[-2]:
                self.sell()
            elif self.rsi[-1] < 100 - self.entry_rsi and self.atr[-1] < self.atr[-2]:
                self.buy()
        else:
            if self.position.is_long and self.rsi[-1] > self.exit_rsi:
                self.position.close()
            elif self.position.is_short and self.rsi[-1] < 100 - self.exit_rsi:
                self.position.close()
