from backtesting import Backtest, Strategy
import pandas as pd
import talib
import logging
from datetime import datetime

class PivotPointsStrategy(Strategy):
    """
    Pivot Points Strategy with Filters
    
    Entry Rules:
    1. Long: Price breaks above pivot point with confirmation
    2. Short: Price breaks below pivot point with confirmation
    
    Exit Rules:
    1. Long: Price breaks below S1 or stop loss hit
    2. Short: Price breaks above R1 or stop loss hit
    
    Parameters:
    - confirmation_periods: Number of periods for confirmation
    - stop_loss_pct: Stop loss percentage (overridden by S1/R1 or ATR)
    - take_profit_pct: Take profit percentage (overridden by R1/S1)
    - use_atr_sl: Boolean to use ATR for stop loss instead of S1/R1
    - atr_period: Period for ATR calculation
    - atr_multiplier: ATR multiplier for stop loss
    - ema_period: Period for EMA trend filter
    - rsi_period: Period for RSI calculation
    - rsi_ob: RSI Overbought threshold
    - rsi_os: RSI Oversold threshold
    """
    
    # Strategy parameters
    confirmation_periods = 2
    stop_loss_pct = 0.05
    take_profit_pct = 0.10
    use_atr_sl = False
    atr_period = 14
    atr_multiplier = 1.5
    ema_period = 50
    rsi_period = 14
    rsi_ob = 70
    rsi_os = 30
    
    def init(self):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        try:
            # Calculate previous day's high, low, and close
            self.prev_high = self.data.High.shift(1)
            self.prev_low = self.data.Low.shift(1)
            self.prev_close = self.data.Close.shift(1)
            
            # Calculate pivot points
            self.pp = self.I(lambda: (self.prev_high + self.prev_low + self.prev_close) / 3)
            self.r1 = self.I(lambda: 2 * self.pp - self.prev_low)
            self.s1 = self.I(lambda: 2 * self.pp - self.prev_high)
            self.r2 = self.I(lambda: self.pp + (self.prev_high - self.prev_low))
            self.s2 = self.I(lambda: self.pp - (self.prev_high - self.prev_low))
            
            # Calculate EMA Filter
            self.ema = self.I(talib.EMA, self.data.Close, self.ema_period)

            # Calculate RSI
            self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)

            # Calculate OBV
            self.obv = self.I(talib.OBV, self.data.Close, self.data.Volume)

            # Calculate ATR
            self.atr = self.I(talib.ATR, self.data.High, self.data.Low, 
                            self.data.Close, self.atr_period)
            
            self.logger.info("Strategy initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error in init(): {str(e)}")
            raise
        
    def next(self):
        try:
            # Skip if not enough data for indicators or pivots
            if len(self.data) < max(self.confirmation_periods, self.ema_period, self.rsi_period) or pd.isna(self.pp[-1]):
                return
                
            price = self.data.Close[-1]
            
            # Entry conditions
            if not self.position:
                # Long entry: Break PP, confirmed, Price > EMA, RSI not OB, OBV rising
                long_break_confirmed = (price > self.pp[-1] and 
                                      all(self.data.Close[-i] > self.pp[-i] for i in range(1, self.confirmation_periods + 1)))

                if (long_break_confirmed and 
                    price > self.ema[-1] and
                    self.rsi[-1] < self.rsi_ob and
                    self.obv[-1] > self.obv[-2]):
                    
                    # Determine Stop Loss
                    if self.use_atr_sl:
                        atr_value = self.atr[-1]
                        stop_loss = price - (atr_value * self.atr_multiplier)
                    else:
                        stop_loss = self.s1[-1]
                    
                    # Determine Take Profit (using R1 as default)
                    take_profit = self.r1[-1]
                    
                    self.buy(sl=stop_loss, tp=take_profit)
                    self.logger.info(f"Long entry at {price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                    
                # Short entry: Break PP, confirmed, Price < EMA, RSI not OS, OBV falling
                short_break_confirmed = (price < self.pp[-1] and 
                                       all(self.data.Close[-i] < self.pp[-i] for i in range(1, self.confirmation_periods + 1)))

                elif (short_break_confirmed and 
                      price < self.ema[-1] and
                      self.rsi[-1] > self.rsi_os and
                      self.obv[-1] < self.obv[-2]):

                    # Determine Stop Loss
                    if self.use_atr_sl:
                        atr_value = self.atr[-1]
                        stop_loss = price + (atr_value * self.atr_multiplier)
                    else:
                        stop_loss = self.r1[-1]
                    
                    # Determine Take Profit (using S1 as default)
                    take_profit = self.s1[-1]

                    self.sell(sl=stop_loss, tp=take_profit)
                    self.logger.info(f"Short entry at {price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                    
            # Exit conditions
            else:
                if self.position.is_long:
                    if self.data.Close[-1] < self.s1[-1]:
                        self.position.close()
                        self.logger.info(f"Closed long position at {price:.2f}")
                        
                elif self.position.is_short:
                    if self.data.Close[-1] > self.r1[-1]:
                        self.position.close()
                        self.logger.info(f"Closed short position at {price:.2f}")
                        
        except Exception as e:
            self.logger.error(f"Error in next(): {str(e)}")
            raise

"""
Notes for Further Advancement:
1. Add volume confirmation for breakouts - OBV added
2. Implement dynamic position sizing based on pivot range
3. Add trend filter using moving averages - EMA filter added
4. Consider adding RSI for overbought/oversold conditions - RSI added
5. Implement trailing stops based on pivot levels
6. Add multiple timeframe analysis
7. Consider adding correlation filter with other assets
8. Add maximum drawdown protection
9. Implement partial profit taking
10. Add adaptive stop loss based on volatility - ATR based SL option added
11. Consider adding price action patterns for entry confirmation
12. Add risk management for maximum consecutive losses
13. Consider adding Fibonacci extensions for take profit levels
14. Add support/resistance confluence for stronger signals
""" 