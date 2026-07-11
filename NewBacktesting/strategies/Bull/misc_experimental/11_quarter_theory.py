from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib
import logging
from datetime import datetime

class QuarterTheoryStrategy(Strategy):
    """
    Quarter Theory Strategy with Volume, Trend, and RSI filters
    
    Entry Rules:
    1. Long: Price breaks above quarter level, above SMA, RSI not overbought, volume confirmation
    2. Short: Price breaks below quarter level, below SMA, RSI not oversold, volume confirmation
    
    Exit Rules:
    1. Long: Price breaks below previous quarter level or stop loss hit
    2. Short: Price breaks above previous quarter level or stop loss hit
    
    Parameters:
    - confirmation_periods: Number of periods for confirmation
    - stop_loss_pct: Stop loss percentage (now relative to entry)
    - take_profit_pct: Take profit percentage (now relative to entry)
    - quarter_size: Size of each quarter level
    - sma_period: Period for trend-filtering SMA
    - rsi_period: Period for RSI
    - rsi_oversold: RSI oversold level
    - rsi_overbought: RSI overbought level
    - volume_ma_period: Period for Volume MA
    """
    
    # Strategy parameters
    confirmation_periods = 2
    stop_loss_pct = 0.05
    take_profit_pct = 0.10
    quarter_size = 0.25
    sma_period = 50
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70
    volume_ma_period = 20
    
    def init(self):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        try:
            # Calculate quarter levels
            self.quarter_levels = self.I(self.calculate_quarter_levels, self.data.Close)
            
            # Calculate indicators
            self.sma = self.I(talib.SMA, self.data.Close, self.sma_period)
            self.rsi = self.I(talib.RSI, self.data.Close, self.rsi_period)
            self.volume_ma = self.I(talib.SMA, self.data.Volume, self.volume_ma_period)
            
            self.logger.info("Strategy initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error in init(): {str(e)}")
            raise
        
    def next(self):
        try:
            # Skip if not enough data
            if len(self.data) < max(self.confirmation_periods, self.sma_period, 
                                  self.rsi_period, self.volume_ma_period):
                return
                
            # Get current price, volume, indicators and quarter levels
            current_price = self.data.Close[-1]
            current_volume = self.data.Volume[-1]
            current_quarter = self.quarter_levels[-1]
            next_quarter = current_quarter + self.quarter_size
            prev_quarter = current_quarter - self.quarter_size
            
            # Conditions
            price_above_sma = current_price > self.sma[-1]
            price_below_sma = current_price < self.sma[-1]
            rsi_ok_long = self.rsi[-1] < self.rsi_overbought
            rsi_ok_short = self.rsi[-1] > self.rsi_oversold
            volume_conf = current_volume > self.volume_ma[-1]
            
            # Entry conditions
            if not self.position:
                # Long entry: Break above next quarter, above SMA, RSI ok, volume confirmed
                if (current_price > next_quarter and 
                    all(self.data.Close[-self.confirmation_periods:] > next_quarter) and
                    price_above_sma and rsi_ok_long and volume_conf):
                    
                    stop_loss = current_price * (1 - self.stop_loss_pct)
                    take_profit = current_price * (1 + self.take_profit_pct)
                    
                    # Ensure stop loss is not above entry, take profit not below entry
                    stop_loss = min(stop_loss, prev_quarter)
                    take_profit = max(take_profit, next_quarter + self.quarter_size)
                    
                    self.buy(sl=stop_loss, tp=take_profit)
                    self.logger.info(f"Long entry at {current_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                    
                # Short entry: Break below prev quarter, below SMA, RSI ok, volume confirmed
                elif (current_price < prev_quarter and 
                      all(self.data.Close[-self.confirmation_periods:] < prev_quarter) and
                      price_below_sma and rsi_ok_short and volume_conf):
                    
                    stop_loss = current_price * (1 + self.stop_loss_pct)
                    take_profit = current_price * (1 - self.take_profit_pct)
                    
                    # Ensure stop loss is not below entry, take profit not above entry
                    stop_loss = max(stop_loss, next_quarter)
                    take_profit = min(take_profit, prev_quarter - self.quarter_size)
                    
                    self.sell(sl=stop_loss, tp=take_profit)
                    self.logger.info(f"Short entry at {current_price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                    
            # Exit conditions
            else:
                if self.position.is_long:
                    if current_price < current_quarter:
                        self.position.close()
                        self.logger.info(f"Closed long position at {current_price:.2f}")
                        
                elif self.position.is_short:
                    if current_price > current_quarter:
                        self.position.close()
                        self.logger.info(f"Closed short position at {current_price:.2f}")
                        
        except Exception as e:
            self.logger.error(f"Error in next(): {str(e)}")
            raise
            
    @staticmethod
    def calculate_quarter_levels(prices):
        """Calculate quarter levels based on price"""
        # Ensure prices is a pandas Series for numpy functions
        prices_series = pd.Series(prices) 
        return np.floor(prices_series / 0.25) * 0.25

"""
Notes for Further Advancement:
1. Add volume confirmation for breakouts (DONE - Volume MA)
2. Implement dynamic position sizing based on quarter range
3. Add trend filter using moving averages (DONE - SMA)
4. Consider adding RSI for overbought/oversold conditions (DONE)
5. Implement trailing stops based on quarter levels
6. Add multiple timeframe analysis
7. Consider adding correlation filter with other assets
8. Add maximum drawdown protection
9. Implement partial profit taking
10. Add adaptive stop loss based on volatility (e.g., ATR)
11. Consider adding price action patterns for entry confirmation
12. Add risk management for maximum consecutive losses
13. Consider adding Fibonacci extensions for take profit levels
14. Add support/resistance confluence for stronger signals
15. Implement dynamic quarter size based on volatility
16. Add momentum confirmation for quarter level breaks (e.g., MACD, Momentum)
""" 