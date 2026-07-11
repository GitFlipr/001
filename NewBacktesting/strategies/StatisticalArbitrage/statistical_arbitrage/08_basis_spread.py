from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib
import logging
from datetime import datetime


def _basis_from_data(data):
    spot = np.asarray(data.spot, dtype=float)
    futures = np.asarray(data.futures, dtype=float)
    return (futures - spot) / np.maximum(np.abs(spot), 1e-12)


def _rolling_mean(arr, window):
    return pd.Series(arr).rolling(window).mean().to_numpy()


def _rolling_std(arr, window):
    return pd.Series(arr).rolling(window).std().to_numpy()


class BasisSpreadStrategy(Strategy):
    """
    Basis Spread Strategy
    
    Entry Rules:
    1. Long: When futures price > spot price (positive basis)
    2. Short: When futures price < spot price (negative basis)
    
    Exit Rules:
    1. Long: When basis turns negative or stop loss hit
    2. Short: When basis turns positive or stop loss hit
    """
    
    # Strategy parameters
    basis_threshold = 0.01  # 1% minimum basis
    stop_loss_pct = 0.05   # 5% stop loss
    take_profit_pct = 0.10 # 10% take profit
    position_size = 0.1    # 10% of equity per position
    ema_period = 50       # EMA period for trend filter
    
    def init(self):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        try:
            # Validate required data columns
            if 'spot' not in self.data.df.columns or 'futures' not in self.data.df.columns:
                raise ValueError("Data must include 'spot' and 'futures' columns for BasisSpreadStrategy")
            
            if 'volume' not in self.data.df.columns:
                self.logger.warning("'volume' column not found for OBV calculation. Using dummy values.")
                self.data.df['volume'] = 1.0

            # Calculate basis spread
            self.basis = self.I(_basis_from_data, self.data)
            
            # Calculate rolling basis statistics
            self.basis_mean = self.I(_rolling_mean, self.basis, 20)
            self.basis_std = self.I(_rolling_std, self.basis, 20)
            
            # Calculate EMA Filter on spot price
            self.spot_ema = self.I(talib.EMA, self.data.spot, self.ema_period)

            # Calculate OBV on spot price and volume
            self.spot_obv = self.I(talib.OBV, self.data.spot, self.data.volume)
            
            self.logger.info("Strategy initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error in init(): {str(e)}")
            raise
        
    def next(self):
        try:
            # Skip if not enough data for indicators
            if len(self.data) < max(20, self.ema_period):
                return
                
            # Calculate current basis
            current_basis = self.basis[-1]
            current_spot_price = self.data.spot[-1]
            
            # Entry conditions
            if not self.position:
                # Long entry (positive basis, spot price > EMA, spot OBV rising)
                if (current_basis > self.basis_threshold and
                    current_spot_price > self.spot_ema[-1] and
                    self.spot_obv[-1] > self.spot_obv[-2]):
                    
                    stop_loss = current_spot_price * (1 - self.stop_loss_pct)
                    take_profit = current_spot_price * (1 + self.take_profit_pct)
                    
                    self.buy(size=self.position_size, sl=stop_loss, tp=take_profit)
                    self.logger.info(f"Long entry at {current_spot_price:.2f}, Basis: {current_basis:.2%}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                    
                # Short entry (negative basis, spot price < EMA, spot OBV falling)
                elif (current_basis < -self.basis_threshold and
                      current_spot_price < self.spot_ema[-1] and
                      self.spot_obv[-1] < self.spot_obv[-2]):
                    
                    stop_loss = current_spot_price * (1 + self.stop_loss_pct)
                    take_profit = current_spot_price * (1 - self.take_profit_pct)
                    
                    self.sell(size=self.position_size, sl=stop_loss, tp=take_profit)
                    self.logger.info(f"Short entry at {current_spot_price:.2f}, Basis: {current_basis:.2%}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                    
            # Exit conditions
            else:
                if self.position.is_long:
                    if current_basis < 0:  # Basis turned negative
                        self.position.close()
                        self.logger.info(f"Closed long position at {current_spot_price:.2f}, Basis: {current_basis:.2%}")
                        
                elif self.position.is_short:
                    if current_basis > 0:  # Basis turned positive
                        self.position.close()
                        self.logger.info(f"Closed short position at {current_spot_price:.2f}, Basis: {current_basis:.2%}")
                        
        except Exception as e:
            self.logger.error(f"Error in next(): {str(e)}")
            raise

"""
Notes for Further Advancement:
1. Add dynamic basis threshold based on historical volatility
2. Implement position sizing based on basis strength
3. Add volume confirmation - OBV (on spot) added
4. Consider adding moving average filter - EMA (on spot) added
5. Implement trailing stops based on basis movement
6. Add multiple timeframe analysis
7. Consider adding correlation filter with other assets
8. Add maximum drawdown protection
9. Implement partial profit taking
10. Add adaptive basis threshold based on market regime
11. Consider adding funding rate analysis
12. Add risk management for basis convergence/divergence
""" 