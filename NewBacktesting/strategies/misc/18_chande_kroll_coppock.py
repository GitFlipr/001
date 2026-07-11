from backtesting import Backtest, Strategy
import pandas as pd
import talib
import numpy as np
import logging
from datetime import datetime

class ChandeKrollCoppockStrategy(Strategy):
    """
    Chande Kroll Stop + Coppock Curve Strategy with Volume, Trend, RSI, and MACD Filters
    
    Entry Rules:
    1. Long: Price above upper Kroll band, Coppock crosses above zero, price above EMA Trend, RSI not overbought, MACD bullish, volume confirmation.
    2. Short: Price below lower Kroll band, Coppock crosses below zero, price below EMA Trend, RSI not oversold, MACD bearish, volume confirmation.
    
    Exit Rules:
    1. Long: Price crosses below lower Kroll band OR Coppock crosses below zero OR MACD turns bearish.
    2. Short: Price crosses above upper Kroll band OR Coppock crosses above zero OR MACD turns bullish.
    
    Parameters:
    - kroll_period: Period for Kroll Stop High/Low and ATR calculation
    - kroll_multiplier: ATR multiplier for Kroll Stop
    - kroll_lookback: Lookback period for Kroll Stop ATR average (unused in this impl)
    - coppock_fast: Fast period for Coppock Curve WMA
    - coppock_slow: Slow period for Coppock Curve WMA
    - coppock_roc: ROC period for Coppock Curve
    - ema_trend_period: Period for EMA trend filter
    - rsi_period: Period for RSI
    - rsi_oversold: RSI oversold level
    - rsi_overbought: RSI overbought level
    - macd_fast: MACD fast period
    - macd_slow: MACD slow period
    - macd_signal: MACD signal period
    - volume_ma_period: Period for Volume MA
    - stop_loss_pct: Stop loss percentage
    - take_profit_pct: Take profit percentage
    """
    
    # Strategy parameters
    kroll_period = 10
    kroll_multiplier = 1
    kroll_lookback = 9
    coppock_fast = 11
    coppock_slow = 14
    coppock_roc = 10
    ema_trend_period = 50
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    volume_ma_period = 20
    stop_loss_pct = 0.05
    take_profit_pct = 0.10
    
    def init(self):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        try:
            # Calculate ATR for Kroll Stop
            self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.kroll_period)
            
            # Calculate Kroll Stop bands
            self.kroll_high = self.I(lambda x, n: pd.Series(x).rolling(window=n).max(), self.data.High, self.kroll_period, name="Kroll_HH")
            self.kroll_low = self.I(lambda x, n: pd.Series(x).rolling(window=n).min(), self.data.Low, self.kroll_period, name="Kroll_LL")
            self.upper_band = self.I(lambda hh, atr, mult: hh - (mult * atr), self.kroll_high, self.atr, self.kroll_multiplier, name="Kroll_Upper")
            self.lower_band = self.I(lambda ll, atr, mult: ll + (mult * atr), self.kroll_low, self.atr, self.kroll_multiplier, name="Kroll_Lower")

            # Calculate Coppock Curve
            self.coppock = self.I(self.calculate_coppock_curve, self.data.Close, 
                                self.coppock_slow, self.coppock_fast, self.coppock_roc, name="Coppock")

            # Additional Indicators
            self.ema_trend = self.I(talib.EMA, self.data.Close, self.ema_trend_period)
            self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)
            self.macd, self.macdsignal, self.macdhist = self.I(talib.MACD, self.data.Close,
                                                             self.macd_fast, self.macd_slow, self.macd_signal)
            self.volume_ma = self.I(talib.SMA, self.data.Volume, self.volume_ma_period)
            
            self.logger.info("Strategy initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error in init(): {str(e)}")
            raise
        
    def next(self):
        try:
            # Ensure all indicators have enough data
            coppock_min_period = self.coppock_slow + self.coppock_roc - 1
            min_periods = max(self.kroll_period, coppock_min_period, self.ema_trend_period, self.rsi_period,
                            self.macd_slow + self.macd_signal - 1, self.volume_ma_period)
            if len(self.data) < min_periods + 1: # Need previous bar data for crosses
                return

            # Conditions
            price = self.data.Close[-1]
            upper_kroll = self.upper_band[-1]
            lower_kroll = self.lower_band[-1]
            coppock_val = self.coppock[-1]
            coppock_prev = self.coppock[-2]
            ema_trend_val = self.ema_trend[-1]
            rsi_val = self.rsi[-1]
            macd_val = self.macd[-1]
            macdsignal_val = self.macdsignal[-1]
            volume_val = self.data.Volume[-1]
            volume_ma_val = self.volume_ma[-1]

            # Filter conditions
            long_trend_ok = price > ema_trend_val
            short_trend_ok = price < ema_trend_val
            rsi_ok_long = rsi_val < self.rsi_overbought
            rsi_ok_short = rsi_val > self.rsi_oversold
            macd_bullish = macd_val > macdsignal_val
            macd_bearish = macd_val < macdsignal_val
            volume_conf = volume_val > volume_ma_val
            coppock_cross_up = coppock_val > 0 and coppock_prev <= 0
            coppock_cross_down = coppock_val < 0 and coppock_prev >= 0
            
            # Entry conditions
            if not self.position:
                # Long entry
                if (price > upper_kroll and coppock_cross_up and long_trend_ok and 
                    rsi_ok_long and macd_bullish and volume_conf):
                    stop_loss = price * (1 - self.stop_loss_pct)
                    take_profit = price * (1 + self.take_profit_pct)
                    # Alternative SL: lower_kroll
                    self.buy(sl=stop_loss, tp=take_profit)
                    self.logger.info(f"Long entry at {price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                    
                # Short entry
                elif (price < lower_kroll and coppock_cross_down and short_trend_ok and 
                      rsi_ok_short and macd_bearish and volume_conf):
                    stop_loss = price * (1 + self.stop_loss_pct)
                    take_profit = price * (1 - self.take_profit_pct)
                    # Alternative SL: upper_kroll
                    self.sell(sl=stop_loss, tp=take_profit)
                    self.logger.info(f"Short entry at {price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                    
            # Exit conditions
            else:
                if self.position.is_long:
                    if (price < lower_kroll or coppock_val < 0 or macd_bearish):
                        self.position.close()
                        self.logger.info(f"Closed long position at {price:.2f}")
                        
                elif self.position.is_short:
                    if (price > upper_kroll or coppock_val > 0 or macd_bullish):
                        self.position.close()
                        self.logger.info(f"Closed short position at {price:.2f}")
                        
        except Exception as e:
            self.logger.error(f"Error in next(): {str(e)}")
            raise
                    
    @staticmethod
    def calculate_coppock_curve(close, slow_roc_period=14, fast_roc_period=11, wma_period=10):
        """Calculate Coppock Curve using standard definition with TA-Lib functions where possible."""
        close = pd.Series(close) # Ensure Series for ROC/WMA
        # Calculate ROC for slow and fast periods
        roc_slow = talib.ROC(close, timeperiod=slow_roc_period)
        roc_fast = talib.ROC(close, timeperiod=fast_roc_period)
        
        # Sum of ROCs
        roc_sum = roc_slow + roc_fast
        
        # Calculate Coppock Curve (WMA of the sum of ROCs)
        coppock = talib.WMA(roc_sum, timeperiod=wma_period)
        return coppock

"""
Notes for Further Advancement:
1. Add volume confirmation for signals (DONE - Volume MA)
2. Implement dynamic position sizing based on band width or volatility
3. Add trend filter using multiple EMAs (DONE - EMA Trend)
4. Consider adding RSI for overbought/oversold conditions (DONE)
5. Implement trailing stops based on ATR or Kroll Bands
6. Add multiple timeframe analysis
7. Consider adding correlation filter with other assets
8. Add maximum drawdown protection
9. Implement partial profit taking
10. Add adaptive stop loss based on volatility (e.g., ATR)
11. Consider adding price action patterns for entry confirmation
12. Add risk management for maximum consecutive losses
13. Consider adding MACD for trend confirmation (DONE)
14. Add support/resistance confluence for stronger signals
15. Implement dynamic Coppock Curve thresholds based on volatility (e.g., +/- std dev)
16. Add momentum confirmation for band breaks (e.g., Momentum indicator)
17. Consider adding volume profile for stronger signals
18. Add risk management for maximum position size
19. Consider adding Fibonacci retracement levels
20. Add risk management for maximum daily loss
""" 