import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import talib

class Mean_Reversion_Low_Vol(Strategy):
    # Strategy parameters
    bb_period = 20
    bb_std = 2.0
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30
    atr_period = 14
    atr_multiplier = 1.5
    volume_sma_period = 20

    def init(self):
        # Initialize indicators
        # Bollinger Bands
        self.upper_band, self.middle_band, self.lower_band = self.I(
            talib.BBANDS, self.data.Close, timeperiod=self.bb_period,  # type: ignore
            nbdevup=self.bb_std, nbdevdn=self.bb_std, matype=0
        )
        
        # ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)  # type: ignore
        
        # RSI for overbought/oversold confirmation
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)  # type: ignore
        
        # Volume SMA for volume confirmation
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_sma_period)

    def next(self):
        # Get current values
        price = self.data.Close[-1]
        volume = self.data.Volume[-1]
        
        # Skip if we don't have enough data
        if (np.isnan(self.upper_band[-1]) or np.isnan(self.lower_band[-1]) or  # type: ignore
            np.isnan(self.middle_band[-1]) or np.isnan(self.atr[-1]) or  # type: ignore
            np.isnan(self.rsi[-1]) or np.isnan(self.volume_sma[-1])):  # type: ignore
            return

        # Long entry conditions - price below lower band with oversold RSI
        long_condition = (
            price < self.lower_band[-1] and  # Price below lower band  # type: ignore
            self.rsi[-1] < self.rsi_oversold and  # Oversold RSI  # type: ignore
            volume > self.volume_sma[-1] * 0.8  # Reasonable volume  # type: ignore
        )
        
        # Short entry conditions - price above upper band with overbought RSI
        short_condition = (
            price > self.upper_band[-1] and  # Price above upper band  # type: ignore
            self.rsi[-1] > self.rsi_overbought and  # Overbought RSI  # type: ignore
            volume > self.volume_sma[-1] * 0.8  # Reasonable volume  # type: ignore
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
            # Exit long if price moves above middle band or RSI becomes overbought
            if price > self.middle_band[-1] or self.rsi[-1] > self.rsi_overbought:  # type: ignore
                self.position.close()
                
        elif self.position.is_short:
            # Exit short if price moves below middle band or RSI becomes oversold
            if price < self.middle_band[-1] or self.rsi[-1] < self.rsi_oversold:  # type: ignore
                self.position.close()
