from backtesting import Backtest, Strategy
import pandas as pd
import talib
import numpy as np
import logging

class TrendFollowingScalpingStrategy(Strategy):
    """
    Trend Following Scalping Strategy Template
    
    Entry Rules:
    1. Long: 
       - Price above 200 SMA (trend confirmation)
       - Pullback to 20 EMA
       - RSI < 30 (oversold)
       - Volume above average
       - ADX > 25 (strong trend)
       
    2. Short:
       - Price below 200 SMA (trend confirmation)
       - Pullback to 20 EMA
       - RSI > 70 (overbought)
       - Volume above average
       - ADX > 25 (strong trend)
    
    Exit Rules:
    1. Long: 
       - Price reaches 20 EMA
       - RSI > 70
       - ADX < 20
       - Trailing stop hit
       
    2. Short:
       - Price reaches 20 EMA
       - RSI < 30
       - ADX < 20
       - Trailing stop hit
    
    Parameters:
    - sma_period: Period for trend SMA
    - ema_period: Period for pullback EMA
    - rsi_period: Period for RSI
    - adx_period: Period for ADX
    - volume_ma_period: Period for volume MA
    - trailing_stop_atr: ATR multiplier for trailing stop
    - risk_per_trade: Risk percentage per trade
    """
    
    sma_period = 200
    ema_period = 20
    rsi_period = 14
    adx_period = 14
    volume_ma_period = 20
    trailing_stop_atr = 2.0
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Calculate trend indicators
        self.sma = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_period)
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        
        # Calculate momentum indicators
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close,
                         timeperiod=self.adx_period)
        
        # Calculate volume indicators
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_ma_period)
        
        # Calculate ATR for trailing stop
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close,
                         timeperiod=14)
    
    def next(self):
        # Skip if not enough data
        if len(self.data) < max(self.sma_period, self.ema_period, self.rsi_period, self.adx_period):
            return
            
        price = self.data.Close[-1]
        volume = self.data.Volume[-1]
        
        # Check volume surge
        volume_surge = volume > self.volume_ma[-1]
        
        # Check trend strength
        strong_trend = self.adx[-1] > 25
        
        # Position management
        if not self.position:
            # Calculate position size based on ATR
            atr = self.atr[-1]
            risk_amount = self.equity * self.risk_per_trade
            position_size = risk_amount / (atr * self.trailing_stop_atr)
            
            # Long entry
            if (price > self.sma[-1] and  # Uptrend
                price <= self.ema[-1] and  # Pullback to EMA
                self.rsi[-1] < 30 and  # Oversold
                volume_surge and  # Volume confirmation
                strong_trend):  # Strong trend
                
                stop_loss = price - (atr * self.trailing_stop_atr)
                self.buy(size=position_size, sl=stop_loss)
                logging.info(f"Long entry at {price:.2f}, Stop loss at {stop_loss:.2f}")
                
            # Short entry
            elif (price < self.sma[-1] and  # Downtrend
                  price >= self.ema[-1] and  # Pullback to EMA
                  self.rsi[-1] > 70 and  # Overbought
                  volume_surge and  # Volume confirmation
                  strong_trend):  # Strong trend
                
                stop_loss = price + (atr * self.trailing_stop_atr)
                self.sell(size=position_size, sl=stop_loss)
                logging.info(f"Short entry at {price:.2f}, Stop loss at {stop_loss:.2f}")
                
        # Exit conditions
        else:
            if self.position.is_long:
                # Exit conditions
                if (price >= self.ema[-1] or  # Price reaches EMA
                    self.rsi[-1] > 70 or  # Overbought
                    self.adx[-1] < 20):  # Weak trend
                    self.position.close()
                    logging.info(f"Long exit at {price:.2f}")
                    
            elif self.position.is_short:
                # Exit conditions
                if (price <= self.ema[-1] or  # Price reaches EMA
                    self.rsi[-1] < 30 or  # Oversold
                    self.adx[-1] < 20):  # Weak trend
                    self.position.close()
                    logging.info(f"Short exit at {price:.2f}")

"""
Notes for Further Advancement:
1. Add multiple timeframe trend confirmation
2. Implement dynamic position sizing based on trend strength
3. Add volume profile analysis
4. Consider adding momentum divergence
5. Implement adaptive trailing stops
6. Add time-based filters for high-volatility periods
7. Consider adding support/resistance levels
8. Implement dynamic risk adjustment
9. Add correlation analysis with sector/market
10. Consider adding order flow analysis
11. Implement smart take-profit levels
12. Add maximum adverse excursion tracking
13. Consider adding sentiment indicators
14. Implement trade clustering analysis
15. Add volatility regime detection
16. Consider adding mean reversion filters
17. Implement position scaling based on conviction
18. Add trend exhaustion signals
19. Consider adding price action patterns
20. Implement advanced money management
""" 