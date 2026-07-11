from backtesting import Strategy
import pandas as pd
import numpy as np
import talib
import logging
from datetime import datetime

class SwingTradeStrategy(Strategy):
    """
    Enhanced Swing Trade Strategy with Ichimoku Cloud, Fibonacci retracements and multi-factor entry/exit confirmation
    
    Entry Rules:
    1. Long:
       - Price above Ichimoku Cloud (bullish trend)
       - Price pulls back to key Fibonacci level (38.2% or 50% of recent swing)
       - Weekly RSI above 40 (bullish momentum)
       - Daily MACD histogram turning up (momentum confirmation)
       - Volume increasing on bullish candles
       - Price above 50-day EMA (trend confirmation)
    
    2. Short:
       - Price below Ichimoku Cloud (bearish trend)
       - Price rallies to key Fibonacci level (38.2% or 50% of recent swing)
       - Weekly RSI below 60 (bearish momentum)
       - Daily MACD histogram turning down (momentum confirmation)
       - Volume increasing on bearish candles
       - Price below 50-day EMA (trend confirmation)
    
    Exit Rules:
    1. Long:
       - Price reaches measured target (Fibonacci extension levels)
       - Weekly RSI reaches overbought (>70)
       - Daily MACD turns bearish
       - Price breaks below trailing stop (ATR-based)
       - Price breaks below Ichimoku Cloud
    
    2. Short:
       - Price reaches measured target (Fibonacci extension levels)
       - Weekly RSI reaches oversold (<30)
       - Daily MACD turns bullish
       - Price breaks above trailing stop (ATR-based)
       - Price breaks above Ichimoku Cloud
    
    Position sizing is risk-based, typically risking 1-2% of account per trade.
    Stop loss is placed below recent swing low for longs, above recent swing high for shorts.
    
    Parameters:
    - lookback: Period to find swings for Fibonacci calculations
    - ichimoku_tenkan: Tenkan-sen (conversion line) period
    - ichimoku_kijun: Kijun-sen (base line) period
    - ichimoku_senkou_span_b: Senkou Span B (leading span B) period
    - ema_fast: Fast EMA period
    - ema_slow: Slow EMA period
    - rsi_period: RSI calculation period
    - rsi_overbought: RSI overbought level
    - rsi_oversold: RSI oversold level
    - macd_fast: MACD fast period
    - macd_slow: MACD slow period
    - macd_signal: MACD signal period
    - atr_period: ATR calculation period
    - trailing_stop_atr: ATR multiplier for trailing stop
    - risk_per_trade: Risk percentage per trade
    """
    
    # Trend/Momentum Parameters
    lookback = 20            # Period to find swing highs/lows
    ichimoku_tenkan = 9      # Conversion line period
    ichimoku_kijun = 26      # Base line period
    ichimoku_senkou_span_b = 52  # Leading span B period
    ema_fast = 20            # Fast EMA period (20-day)
    ema_slow = 50            # Slow EMA period (50-day)
    
    # Momentum Indicators
    rsi_period = 14          # RSI period
    rsi_overbought = 70      # RSI overbought level
    rsi_oversold = 30        # RSI oversold level
    macd_fast = 12           # MACD fast period
    macd_slow = 26           # MACD slow period
    macd_signal = 9          # MACD signal period
    
    # Risk Management
    atr_period = 14          # ATR period
    trailing_stop_atr = 2.5  # ATR multiplier for trailing stop
    risk_per_trade = 0.015   # 1.5% risk per trade
    
    # Fibonacci retracement levels (standard levels)
    fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    
    def init(self):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        try:
            # Ichimoku Cloud components
            self.tenkan = self.I(self._ichimoku_tenkan_sen, self.data.High, self.data.Low, self.ichimoku_tenkan)
            self.kijun = self.I(self._ichimoku_kijun_sen, self.data.High, self.data.Low, self.ichimoku_kijun)
            self.senkou_span_a = self.I(self._senkou_span_a, self.tenkan, self.kijun)
            self.senkou_span_b = self.I(self._senkou_span_b, self.data.High, self.data.Low, self.ichimoku_senkou_span_b)
            
            # Create offset for Senkou Span A and B (26 periods forward)
            self.senkou_span_a_offset = self.I(self._offset, self.senkou_span_a, self.ichimoku_kijun)
            self.senkou_span_b_offset = self.I(self._offset, self.senkou_span_b, self.ichimoku_kijun)
            
            # Moving Averages
            self.ema_fast_line = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_fast)
            self.ema_slow_line = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_slow)
            
            # RSI
            self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
            
            # MACD
            self.macd, self.macd_signal, self.macd_hist = self.I(talib.MACD, self.data.Close, 
                                                               fastperiod=self.macd_fast, 
                                                               slowperiod=self.macd_slow, 
                                                               signalperiod=self.macd_signal)
            
            # ATR for volatility measurement and stop placement
            self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, 
                             timeperiod=self.atr_period)
            
            # Swing point detection
            self.swing_high = self.I(self._find_swing_high, self.data.High, self.lookback)
            self.swing_low = self.I(self._find_swing_low, self.data.Low, self.lookback)
            
            # Fibonacci Retracements (calculated in next() method based on recent swings)
            self.fib_retracements = None
            self.fib_extensions = None
            
            # Volume analysis
            self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
            
            self.logger.info("Strategy initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error in init(): {str(e)}")
            raise
        
    def _ichimoku_tenkan_sen(self, high, low, period):
        """Calculate Tenkan-sen (Conversion Line): (highest high + lowest low)/2 for the past 9 periods"""
        if len(high) < period:
            return np.nan
        return (max(high[-period:]) + min(low[-period:])) / 2
        
    def _ichimoku_kijun_sen(self, high, low, period):
        """Calculate Kijun-sen (Base Line): (highest high + lowest low)/2 for the past 26 periods"""
        if len(high) < period:
            return np.nan
        return (max(high[-period:]) + min(low[-period:])) / 2
    
    def _senkou_span_a(self, tenkan, kijun):
        """Calculate Senkou Span A (Leading Span A): (Tenkan-sen + Kijun-sen)/2"""
        if np.isnan(tenkan) or np.isnan(kijun):
            return np.nan
        return (tenkan + kijun) / 2
    
    def _senkou_span_b(self, high, low, period):
        """Calculate Senkou Span B (Leading Span B): (highest high + lowest low)/2 for the past 52 periods"""
        if len(high) < period:
            return np.nan
        return (max(high[-period:]) + min(low[-period:])) / 2
    
    def _offset(self, value, periods):
        """Offset the value (used for shifting Senkou Span A and B forward)"""
        if len(value) <= periods:
            return value[0]
        return value[-periods]
    
    def _find_swing_high(self, high, lookback):
        """Identify swing highs for Fibonacci retracement calculations"""
        if len(high) < lookback * 2:
            return 0
            
        middle_idx = lookback
        middle_value = high[-middle_idx]
        
        is_swing_high = all(middle_value >= high[-i] for i in range(1, middle_idx)) and \
                        all(middle_value >= high[-(middle_idx+i)] for i in range(1, middle_idx+1))
                        
        return middle_value if is_swing_high else 0
    
    def _find_swing_low(self, low, lookback):
        """Identify swing lows for Fibonacci retracement calculations"""
        if len(low) < lookback * 2:
            return 0
            
        middle_idx = lookback
        middle_value = low[-middle_idx]
        
        is_swing_low = all(middle_value <= low[-i] for i in range(1, middle_idx)) and \
                       all(middle_value <= low[-(middle_idx+i)] for i in range(1, middle_idx+1))
                       
        return middle_value if is_swing_low else float('inf')
    
    def _calculate_fibonacci_levels(self):
        """Calculate Fibonacci retracement and extension levels based on recent swing high/low"""
        try:
            recent_swing_high = 0
            recent_swing_low = float('inf')
            
            # Find most recent valid swing high and low
            for i in range(len(self.data)-1, -1, -1):
                if self.swing_high[i] > 0:
                    recent_swing_high = self.swing_high[i]
                    break
                    
            for i in range(len(self.data)-1, -1, -1):
                if self.swing_low[i] < float('inf'):
                    recent_swing_low = self.swing_low[i]
                    break
            
            if recent_swing_high == 0 or recent_swing_low == float('inf'):
                return None, None
            
            # Calculate retracement levels
            retracements = {}
            for level in self.fib_levels:
                retracements[level] = recent_swing_high - (recent_swing_high - recent_swing_low) * level
            
            # Calculate extension levels
            extensions = {}
            for level in self.fib_levels:
                extensions[level] = recent_swing_high + (recent_swing_high - recent_swing_low) * level
            
            return retracements, extensions
            
        except Exception as e:
            self.logger.error(f"Error calculating Fibonacci levels: {str(e)}")
            return None, None
    
    def _is_near_fibonacci_level(self, price, tolerance_pct=0.01):
        """Check if price is near any Fibonacci level"""
        if self.fib_retracements is None:
            return False
            
        for level, value in self.fib_retracements.items():
            if abs(price - value) / value <= tolerance_pct:
                return True
        return False
    
    def _check_ichimoku_trend(self):
        """Check if price is above/below Ichimoku Cloud"""
        try:
            price = self.data.Close[-1]
            cloud_top = max(self.senkou_span_a_offset[-1], self.senkou_span_b_offset[-1])
            cloud_bottom = min(self.senkou_span_a_offset[-1], self.senkou_span_b_offset[-1])
            
            if price > cloud_top:
                return "bullish"
            elif price < cloud_bottom:
                return "bearish"
            else:
                return "neutral"
                
        except Exception as e:
            self.logger.error(f"Error checking Ichimoku trend: {str(e)}")
            return "neutral"
    
    def _is_volume_confirming(self, direction):
        """Check if volume confirms the price direction"""
        try:
            current_volume = self.data.Volume[-1]
            volume_ma = self.volume_sma[-1]
            
            if direction == "bullish":
                return current_volume > volume_ma and self.data.Close[-1] > self.data.Open[-1]
            elif direction == "bearish":
                return current_volume > volume_ma and self.data.Close[-1] < self.data.Open[-1]
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking volume confirmation: {str(e)}")
            return False
    
    def next(self):
        try:
            # Skip if not enough data
            min_periods = max(self.ichimoku_tenkan, self.ichimoku_kijun, self.ichimoku_senkou_span_b,
                            self.ema_fast, self.ema_slow, self.rsi_period,
                            self.macd_slow + self.macd_signal - 1, self.atr_period)
            
            if len(self.data) < min_periods + 1:
                return
            
            # Calculate Fibonacci levels
            self.fib_retracements, self.fib_extensions = self._calculate_fibonacci_levels()
            
            # Current price and indicators
            price = self.data.Close[-1]
            atr = self.atr[-1]
            
            # Check trend direction
            ichimoku_trend = self._check_ichimoku_trend()
            
            # Check MACD crossover
            macd_bullish = (self.macd[-1] > self.macd_signal[-1] and 
                           self.macd[-2] <= self.macd_signal[-2])
            macd_bearish = (self.macd[-1] < self.macd_signal[-1] and 
                           self.macd[-2] >= self.macd_signal[-2])
            
            # Position management
            if not self.position:
                # Calculate position size based on ATR
                risk_amount = self.equity * self.risk_per_trade
                position_size = risk_amount / (atr * 3)  # Use 3 ATR for initial stop
                
                # Long entry conditions
                if (ichimoku_trend == "bullish" and
                    self._is_near_fibonacci_level(price) and
                    self.rsi[-1] > 40 and
                    (macd_bullish or self.macd_hist[-1] > self.macd_hist[-2]) and
                    self._is_volume_confirming("bullish") and
                    price > self.ema_slow_line[-1]):
                    
                    stop_loss = price - (atr * 3)
                    self.buy(size=position_size, sl=stop_loss)
                    self.logger.info(f"Long entry at {price:.2f}, RSI: {self.rsi[-1]:.2f}, Stop loss at {stop_loss:.2f}")
                
                # Short entry conditions
                elif (ichimoku_trend == "bearish" and
                      self._is_near_fibonacci_level(price) and
                      self.rsi[-1] < 60 and
                      (macd_bearish or self.macd_hist[-1] < self.macd_hist[-2]) and
                      self._is_volume_confirming("bearish") and
                      price < self.ema_slow_line[-1]):
                    
                    stop_loss = price + (atr * 3)
                    self.sell(size=position_size, sl=stop_loss)
                    self.logger.info(f"Short entry at {price:.2f}, RSI: {self.rsi[-1]:.2f}, Stop loss at {stop_loss:.2f}")
            
            # Exit conditions
            else:
                if self.position.is_long:
                    # Update trailing stop based on ATR
                    current_stop = self.position.sl
                    new_stop = price - (atr * self.trailing_stop_atr)
                    
                    if new_stop > current_stop:
                        self.position.sl = new_stop
                        self.logger.info(f"Updated long trailing stop to {new_stop:.2f}")
                    
                    # Exit conditions
                    if (self.rsi[-1] > self.rsi_overbought or
                        macd_bearish or
                        ichimoku_trend == "bearish"):
                        
                        self.position.close()
                        self.logger.info(f"Long exit at {price:.2f}")
                
                elif self.position.is_short:
                    # Update trailing stop based on ATR
                    current_stop = self.position.sl
                    new_stop = price + (atr * self.trailing_stop_atr)
                    
                    if new_stop < current_stop:
                        self.position.sl = new_stop
                        self.logger.info(f"Updated short trailing stop to {new_stop:.2f}")
                    
                    # Exit conditions
                    if (self.rsi[-1] < self.rsi_oversold or
                        macd_bullish or
                        ichimoku_trend == "bullish"):
                        
                        self.position.close()
                        self.logger.info(f"Short exit at {price:.2f}")
                        
        except Exception as e:
            self.logger.error(f"Error in next(): {str(e)}")
            raise

"""
Strategy Enhancement Opportunities:
1. Advanced multi-timeframe analysis requiring higher timeframe data imported and processed
2. Weekly and monthly pivots for additional support/resistance levels
3. Integration of market sentiment indicators
4. Seasonality analysis
5. Add correlation with market indices or sector benchmarks
6. Integration of earnings event risk management
7. Add volatility expansion/contraction filters
8. Economic calendar event risk management
9. Position scaling-in and scaling-out logic
10. Time of day/session-based filters
""" 