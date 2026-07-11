from backtesting import Backtest, Strategy
import pandas as pd
import talib
import numpy as np
import logging

class BBStochRSIScalpingStrategy(Strategy):
    """
    Bollinger Bands + Stochastic RSI Scalping Strategy Template
    
    Entry Rules:
    1. Long: 
       - Price touches lower Bollinger Band
       - Stochastic RSI < 20
       - Price momentum positive (ROC > 0)
       - Volume surge confirmation
       
    2. Short:
       - Price touches upper Bollinger Band
       - Stochastic RSI > 80
       - Price momentum negative (ROC < 0)
       - Volume surge confirmation
    
    Exit Rules:
    1. Long: 
       - Price reaches middle Bollinger Band
       - Stochastic RSI > 80
       - Trailing stop hit
       
    2. Short:
       - Price reaches middle Bollinger Band
       - Stochastic RSI < 20
       - Trailing stop hit
    
    Parameters:
    - bb_period: Period for Bollinger Bands
    - bb_std: Standard deviations for Bollinger Bands
    - stoch_rsi_period: Period for Stochastic RSI
    - stoch_period: Period for Stochastic calculation
    - roc_period: Period for Rate of Change
    - volume_ma_period: Period for volume moving average
    - trailing_stop_atr: ATR multiplier for trailing stop
    - risk_per_trade: Risk percentage per trade
    """
    
    bb_period = 20
    bb_std = 2.0
    stoch_rsi_period = 14
    stoch_period = 14
    roc_period = 1
    volume_ma_period = 20
    trailing_stop_atr = 2.0
    risk_per_trade = 0.01  # 1% risk per trade
    
    def init(self):
        # Set up logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Calculate Bollinger Bands
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, 
            self.data.Close, 
            timeperiod=self.bb_period,
            nbdevup=self.bb_std,
            nbdevdn=self.bb_std,
            matype=talib.MA_Type.SMA)
        
        # Calculate Stochastic RSI
        rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.stoch_rsi_period)
        self.stoch_k, self.stoch_d = self.I(talib.STOCH, rsi, rsi, rsi,
                                           fastk_period=self.stoch_period,
                                           slowk_period=3,
                                           slowd_period=3)
        
        # Rate of Change
        self.roc = self.I(talib.ROC, self.data.Close, timeperiod=self.roc_period)
        
        # Volume MA
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_ma_period)
        
        # ATR for trailing stop
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close,
                         timeperiod=14)
    
    def next(self):
        # Skip if not enough data
        if len(self.data) < max(self.bb_period, self.stoch_rsi_period, self.volume_ma_period):
            return
            
        price = self.data.Close[-1]
        volume = self.data.Volume[-1]
        
        # Check volume surge
        volume_surge = volume > (self.volume_ma[-1] * 1.5)
        
        # Calculate band touches
        lower_band_touch = price <= self.bb_lower[-1]
        upper_band_touch = price >= self.bb_upper[-1]
        
        # Position management
        if not self.position:
            # Calculate position size based on ATR
            atr = self.atr[-1]
            risk_amount = self.equity * self.risk_per_trade
            position_size = risk_amount / (atr * self.trailing_stop_atr)
            
            # Long entry
            if (lower_band_touch and 
                self.stoch_k[-1] < 20 and 
                self.roc[-1] > 0 and 
                volume_surge):
                
                stop_loss = price - (atr * self.trailing_stop_atr)
                self.buy(size=position_size, sl=stop_loss)
                logging.info(f"Long entry at {price:.2f}, Stop loss at {stop_loss:.2f}")
                
            # Short entry
            elif (upper_band_touch and 
                  self.stoch_k[-1] > 80 and 
                  self.roc[-1] < 0 and 
                  volume_surge):
                
                stop_loss = price + (atr * self.trailing_stop_atr)
                self.sell(size=position_size, sl=stop_loss)
                logging.info(f"Short entry at {price:.2f}, Stop loss at {stop_loss:.2f}")
                
        # Exit conditions
        else:
            if self.position.is_long:
                # Exit if middle band reached or overbought
                if (price >= self.bb_middle[-1] or 
                    self.stoch_k[-1] > 80):
                    self.position.close()
                    logging.info(f"Long exit at {price:.2f}")
                    
            elif self.position.is_short:
                # Exit if middle band reached or oversold
                if (price <= self.bb_middle[-1] or 
                    self.stoch_k[-1] < 20):
                    self.position.close()
                    logging.info(f"Short exit at {price:.2f}")

"""
Notes for Further Advancement:
1. Add Bollinger Band width for volatility measurement
2. Implement dynamic BB standard deviation based on volatility
3. Add trend filter using multiple timeframe analysis
4. Consider adding momentum divergence confirmation
5. Implement adaptive Stochastic RSI thresholds
6. Add time-based filters for high-volatility periods
7. Consider adding support/resistance levels
8. Implement dynamic position sizing based on volatility
9. Add correlation analysis with sector/market
10. Consider adding volume profile analysis
11. Implement smart take-profit levels
12. Add maximum adverse excursion tracking
13. Consider adding sentiment indicators
14. Implement dynamic risk adjustment
15. Add trade clustering analysis
16. Consider adding order flow analysis
17. Implement advanced money management
18. Add volatility regime detection
19. Consider adding mean reversion filters
20. Implement position scaling based on conviction
""" 