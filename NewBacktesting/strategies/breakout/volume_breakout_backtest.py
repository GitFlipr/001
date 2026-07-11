import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import talib

def compute_volume_sma(volume, period):
    """Compute volume simple moving average"""
    return pd.Series(volume).rolling(window=period).mean().values

class Volume_Breakout(Strategy):
    # Strategy parameters
    bb_period = 20
    bb_std = 2.0
    obv_period = 20
    volume_sma_period = 20
    min_volume_multiplier = 2.0
    atr_period = 14
    atr_multiplier = 2.0

    def init(self):
        # Initialize indicators
        # Bollinger Bands
        self.upper_band, self.middle_band, self.lower_band = self.I(
            talib.BBANDS, self.data.Close, timeperiod=self.bb_period,  # type: ignore
            nbdevup=self.bb_std, nbdevdn=self.bb_std, matype=0
        )
        
        # ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)  # type: ignore
        
        # Volume SMA
        self.volume_sma = self.I(compute_volume_sma, self.data.Volume, self.volume_sma_period)
        
        # OBV (On Balance Volume) for volume trend confirmation
        self.obv = self.I(talib.OBV, self.data.Close, self.data.Volume)  # type: ignore

    def next(self):
        # Get current values
        price = self.data.Close[-1]
        volume = self.data.Volume[-1]
        
        # Skip if we don't have enough data
        if (np.isnan(self.upper_band[-1]) or np.isnan(self.lower_band[-1]) or  # type: ignore
            np.isnan(self.atr[-1]) or np.isnan(self.volume_sma[-1]) or  # type: ignore
            np.isnan(self.obv[-1])):  # type: ignore
            return

        # Long entry conditions - breakout above upper band with high volume
        long_condition = (
            price > self.upper_band[-1] and  # Price breaks above upper band  # type: ignore
            volume > self.volume_sma[-1] * self.min_volume_multiplier and  # High volume  # type: ignore
            self.obv[-1] > self.obv[-2]  # Increasing OBV (bullish volume)  # type: ignore
        )
        
        # Short entry conditions - breakout below lower band with high volume
        short_condition = (
            price < self.lower_band[-1] and  # Price breaks below lower band  # type: ignore
            volume > self.volume_sma[-1] * self.min_volume_multiplier and  # High volume  # type: ignore
            self.obv[-1] < self.obv[-2]  # Decreasing OBV (bearish volume)  # type: ignore
        )

        # Entry logic
        if not self.position:
            if long_condition:
                # Calculate stop loss and take profit
                stop_loss = price - (self.atr[-1] * self.atr_multiplier)  # type: ignore
                take_profit = price + (2 * (price - stop_loss))  # 2:1 risk-reward
                self.buy(sl=stop_loss, tp=take_profit)
                
            elif short_condition:
                # Calculate stop loss and take profit
                stop_loss = price + (self.atr[-1] * self.atr_multiplier)  # type: ignore
                take_profit = price - (2 * (stop_loss - price))  # 2:1 risk-reward
                self.sell(sl=stop_loss, tp=take_profit)

        # Exit conditions
        elif self.position.is_long:
            # Exit long if price falls back below middle band or volume decreases
            if price < self.middle_band[-1] or volume < self.volume_sma[-1]:  # type: ignore
                self.position.close()
                
        elif self.position.is_short:
            # Exit short if price rises back above middle band or volume decreases
            if price > self.middle_band[-1] or volume < self.volume_sma[-1]:  # type: ignore
                self.position.close()
