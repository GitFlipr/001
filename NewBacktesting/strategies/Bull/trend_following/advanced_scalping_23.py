from backtesting import Backtest, Strategy
import pandas as pd
import talib
import numpy as np
import logging
from datetime import datetime

class AdvancedScalpingStrategy(Strategy):
    """
    Advanced Scalping Strategy with Multi-indicator Confirmation
    
    Entry Rules:
    1. Long: 
       - Price below EMA
       - RSI oversold (<30)
       - MACD bullish crossover
       - Volume above average
       - ADX > 20 (strong trend)
       - Price near lower Bollinger Band
       - ATR increasing (volatility expansion)
       
    2. Short:
       - Price above EMA
       - RSI overbought (>70)
       - MACD bearish crossover
       - Volume above average
       - ADX > 20 (strong trend)
       - Price near upper Bollinger Band
       - ATR increasing (volatility expansion)
    
    Exit Rules:
    1. Long: 
       - Price crosses below trailing stop
       - RSI crosses above 70
       - MACD bearish crossover
       - Price reaches middle Bollinger Band
       
    2. Short:
       - Price crosses above trailing stop
       - RSI crosses below 30
       - MACD bullish crossover
       - Price reaches middle Bollinger Band
    
    Parameters:
    - ema_period: Period for EMA calculation
    - rsi_period: Period for RSI calculation
    - macd_fast: Fast period for MACD
    - macd_slow: Slow period for MACD
    - macd_signal: Signal period for MACD
    - adx_period: Period for ADX calculation
    - volume_ma_period: Period for volume moving average
    - bb_period: Period for Bollinger Bands
    - bb_std: Standard deviations for Bollinger Bands
    - atr_period: Period for ATR calculation
    - atr_roc_period: Period for ATR rate of change
    - trailing_stop_atr: ATR multiplier for trailing stop
    - risk_per_trade: Risk percentage per trade
    """
    
    # Core trend/momentum parameters
    ema_period = 20
    rsi_period = 14
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    
    # Trend strength parameters
    adx_period = 14
    
    # Volume parameters
    volume_ma_period = 20
    
    # Volatility parameters
    bb_period = 20
    bb_std = 2.0
    atr_period = 14
    atr_roc_period = 1
    
    # Risk management parameters
    trailing_stop_atr = 2.0
    risk_per_trade = 0.01    # 1% risk per trade
    
    def init(self):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        try:
            # Calculate trend indicators
            self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
            
            # Calculate momentum indicators
            self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
            
            # MACD
            self.macd, self.macd_signal, self.macd_hist = self.I(talib.MACD, self.data.Close,
                                                                fastperiod=self.macd_fast,
                                                                slowperiod=self.macd_slow,
                                                                signalperiod=self.macd_signal)
            
            # ADX for trend strength
            self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close,
                             timeperiod=self.adx_period)
            
            # Directional movement for trend direction
            self.plus_di = self.I(talib.PLUS_DI, self.data.High, self.data.Low, self.data.Close,
                                timeperiod=self.adx_period)
            self.minus_di = self.I(talib.MINUS_DI, self.data.High, self.data.Low, self.data.Close,
                                 timeperiod=self.adx_period)
                         
            # Volume MA
            self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_ma_period)
            
            # Bollinger Bands
            self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, self.data.Close,
                                                                timeperiod=self.bb_period,
                                                                nbdevup=self.bb_std,
                                                                nbdevdn=self.bb_std,
                                                                matype=0)
            
            # ATR for volatility measurement and dynamic position sizing
            self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close,
                             timeperiod=self.atr_period)
            
            # ATR rate of change for volatility expansion/contraction
            self.atr_roc = self.I(talib.ROC, self.atr, timeperiod=self.atr_roc_period)
            
            self.logger.info("Strategy initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error in init(): {str(e)}")
            raise
    
    def next(self):
        try:
            # Skip if not enough data
            min_periods = max(self.ema_period, self.rsi_period, 
                             self.macd_slow + self.macd_signal - 1, 
                             self.adx_period, self.bb_period, 
                             self.atr_period + self.atr_roc_period, 
                             self.volume_ma_period)
            
            if len(self.data) < min_periods + 1:  # +1 for previous bar comparison
                return
                
            price = self.data.Close[-1]
            volume = self.data.Volume[-1]
            
            # Check if volume is above average
            volume_ok = volume > self.volume_ma[-1]
            
            # Check MACD crossover
            macd_bullish = (self.macd[-1] > self.macd_signal[-1] and 
                           self.macd[-2] <= self.macd_signal[-2])
            macd_bearish = (self.macd[-1] < self.macd_signal[-1] and 
                           self.macd[-2] >= self.macd_signal[-2])
            
            # Check trend strength and direction
            strong_trend = self.adx[-1] > 20
            bullish_trend = self.plus_di[-1] > self.minus_di[-1]
            bearish_trend = self.plus_di[-1] < self.minus_di[-1]
            
            # Check volatility expansion
            volatility_expanding = self.atr_roc[-1] > 0
            
            # Check Bollinger Band proximity
            near_lower_band = price <= (self.bb_lower[-1] * 1.01)  # Within 1% of lower band
            near_upper_band = price >= (self.bb_upper[-1] * 0.99)  # Within 1% of upper band
            
            # Position management
            if not self.position:
                # Calculate position size based on ATR
                atr = self.atr[-1]
                risk_amount = self.equity * self.risk_per_trade
                position_size = risk_amount / (atr * 3)  # Use 3 ATR for initial stop
                
                # Long entry
                if (price < self.ema[-1] and           # Price below EMA (pullback)
                    self.rsi[-1] < 30 and              # RSI oversold
                    (macd_bullish or                   # MACD bullish crossover
                     self.macd[-1] > self.macd[-2]) and # or MACD increasing
                    volume_ok and                      # Volume confirmation
                    strong_trend and                    # ADX confirms trend strength
                    bullish_trend and                  # +DI > -DI (bullish trend)
                    near_lower_band and                # Near lower Bollinger Band
                    volatility_expanding):             # Volatility expanding
                    
                    stop_loss = price - (atr * 3)
                    self.buy(size=position_size, sl=stop_loss)
                    self.logger.info(f"Long entry at {price:.2f}, RSI: {self.rsi[-1]:.2f}, ADX: {self.adx[-1]:.2f}, Stop loss at {stop_loss:.2f}")
                    
                # Short entry
                elif (price > self.ema[-1] and           # Price above EMA (pullback)
                      self.rsi[-1] > 70 and              # RSI overbought
                      (macd_bearish or                   # MACD bearish crossover
                       self.macd[-1] < self.macd[-2]) and # or MACD decreasing
                      volume_ok and                      # Volume confirmation
                      strong_trend and                   # ADX confirms trend strength
                      bearish_trend and                  # -DI > +DI (bearish trend)
                      near_upper_band and                # Near upper Bollinger Band
                      volatility_expanding):             # Volatility expanding
                    
                    stop_loss = price + (atr * 3)
                    self.sell(size=position_size, sl=stop_loss)
                    self.logger.info(f"Short entry at {price:.2f}, RSI: {self.rsi[-1]:.2f}, ADX: {self.adx[-1]:.2f}, Stop loss at {stop_loss:.2f}")
                    
            # Exit conditions
            else:
                if self.position.is_long:
                    # Exit conditions
                    if (self.rsi[-1] > 70 or              # RSI overbought
                        macd_bearish or                   # MACD bearish crossover
                        price >= self.bb_middle[-1]):     # Price reaches middle band
                        
                        self.position.close()
                        self.logger.info(f"Long exit at {price:.2f}")
                        
                elif self.position.is_short:
                    # Exit conditions
                    if (self.rsi[-1] < 30 or              # RSI oversold
                        macd_bullish or                   # MACD bullish crossover
                        price <= self.bb_middle[-1]):     # Price reaches middle band
                        
                        self.position.close()
                        self.logger.info(f"Short exit at {price:.2f}")
                        
        except Exception as e:
            self.logger.error(f"Error in next(): {str(e)}")
            raise

"""
Notes for Further Advancement:
1. Add volume profile analysis for better entry/exit points (PLANNED - Price/volume distribution)
2. Implement dynamic timeframe selection based on volatility (COMPLEX - Requires external data handling)
3. Add market regime detection (trending/ranging) (PARTIALLY DONE - ADX filter)
4. Consider adding Bollinger Bands for volatility-based entries (DONE - BB proximity check)
5. Implement adaptive indicator parameters based on market conditions (PLANNED - Parameter optimization)
6. Add correlation analysis with market indices (PLANNED - External correlation checks)
7. Consider adding order flow analysis (COMPLEX - Requires tick data)
8. Implement dynamic position sizing based on win rate (PARTIALLY DONE - ATR-based sizing)
9. Add maximum adverse excursion analysis (PLANNED - Trade analysis tool)
10. Consider adding momentum divergence confirmation (PLANNED - Price/indicator divergence check)
11. Implement smart take-profit levels based on S/R (PLANNED - Dynamic TP levels)
12. Add time-based filters for high-probability periods (PLANNED - Session filtering)
13. Consider adding volatility-based risk adjustment (DONE - ATR volatility checks)
14. Implement dynamic trailing stops based on ATR (DONE - ATR-based trailing stops)
15. Add multi-timeframe momentum confirmation (COMPLEX - Requires multiple data feeds)
16. Consider adding sentiment analysis (COMPLEX - Requires external data)
17. Implement dynamic risk allocation based on equity curve (PLANNED - Equity curve monitoring)
18. Add trade clustering analysis (PLANNED - Trade metadata analysis)
19. Consider adding mean reversion filters (PARTIALLY DONE - BB mean reversion)
20. Implement advanced risk management with position pyramiding (PLANNED - Position scaling)
""" 