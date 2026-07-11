#!/usr/bin/env python3
"""
Mean Reversion Scalping Strategy

A statistical scalping strategy that trades price deviations from moving averages:
- Bollinger Band mean reversion
- Statistical z-score analysis
- RSI divergence detection
- Volume confirmation
- Dynamic mean reversion thresholds
"""

import pandas as pd
import numpy as np
import talib
import logging
from backtesting import Strategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MeanReversionScalping(Strategy):
    """
    Mean Reversion Scalping Strategy
    
    A statistical scalping strategy that trades price deviations from moving averages:
    - Bollinger Band mean reversion
    - Statistical z-score analysis
    - RSI divergence detection
    - Volume confirmation
    - Dynamic mean reversion thresholds
    """
    
    # Strategy parameters
    risk_per_trade = 0.01          # 1% risk per trade
    max_positions = 2              # Maximum concurrent positions
    max_drawdown = 0.10            # Maximum drawdown limit (10%)
    consecutive_loss_limit = 4      # Maximum consecutive losses
    
    # Mean reversion parameters
    bb_period = 20
    bb_std = 2.0
    z_score_threshold = 2.0        # Z-score threshold for mean reversion
    
    # RSI parameters
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70
    rsi_divergence_lookback = 10
    
    # Moving average parameters
    ma_fast = 10
    ma_slow = 20
    ma_trend = 50
    
    # Volume parameters
    volume_threshold = 1.2
    volume_ma_period = 20
    
    # ATR parameters
    atr_period = 14
    stop_loss_atr_multiplier = 2.0
    take_profit_atr_multiplier = 3.0
    
    # Performance tracking
    track_performance = True
    performance_window = 40         # Performance calculation window
    
    def init(self):
        """Initialize strategy indicators and tracking variables"""
        # Performance tracking
        self.trades_history = []
        self.consecutive_losses = 0
        self.max_equity = self.equity
        self.entry_prices = {}
        self.stop_losses = {}
        self.take_profits = {}
        
        # Core indicators
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, 
                         self.data.Close, timeperiod=self.atr_period)
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_ma_period)
        
        # Bollinger Bands
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, self.data.Close,
                                                             timeperiod=self.bb_period,
                                                             nbdevup=self.bb_std,
                                                             nbdevdn=self.bb_std,
                                                             matype=0)
        
        # RSI
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        
        # Moving averages
        self.ma_fast_line = self.I(talib.SMA, self.data.Close, timeperiod=self.ma_fast)
        self.ma_slow_line = self.I(talib.SMA, self.data.Close, timeperiod=self.ma_slow)
        self.ma_trend_line = self.I(talib.SMA, self.data.Close, timeperiod=self.ma_trend)
        
        # Price statistics for z-score calculation
        self.price_std = self.I(talib.STDDEV, self.data.Close, timeperiod=self.bb_period)
        
        logger.info("MeanReversionScalping initialized successfully")
    
    def calculate_z_score(self) -> float:
        """Calculate current price z-score relative to moving average"""
        if len(self.data) < self.bb_period:
            return 0.0
        
        current_price = self.data.Close[-1]
        current_mean = self.bb_middle[-1]
        current_std = self.price_std[-1]
        
        if current_std > 0:
            z_score = (current_price - current_mean) / current_std
            return z_score
        
        return 0.0
    
    def detect_rsi_divergence(self) -> tuple[bool, bool]:
        """
        Detect RSI divergence for mean reversion signals
        
        Returns:
            tuple: (bullish_divergence, bearish_divergence)
        """
        if len(self.data) < self.rsi_divergence_lookback + 5:
            return False, False
        
        # Look for price making new low/high while RSI doesn't confirm
        lookback_start = max(0, len(self.data) - self.rsi_divergence_lookback)
        
        # Bullish divergence: price makes lower low, RSI makes higher low
        price_lowest = min(self.data.Low[lookback_start:])
        rsi_at_lowest = self.rsi[lookback_start:][np.argmin(self.data.Low[lookback_start:])]
        current_rsi = self.rsi[-1]
        
        bullish_divergence = (self.data.Low[-1] <= price_lowest * 1.001 and  # Price at or below recent low
                             current_rsi > rsi_at_lowest * 1.05)  # RSI higher than at price low
        
        # Bearish divergence: price makes higher high, RSI makes lower high
        price_highest = max(self.data.High[lookback_start:])
        rsi_at_highest = self.rsi[lookback_start:][np.argmax(self.data.High[lookback_start:])]
        
        bearish_divergence = (self.data.High[-1] >= price_highest * 0.999 and  # Price at or above recent high
                             current_rsi < rsi_at_highest * 0.95)  # RSI lower than at price high
        
        return bullish_divergence, bearish_divergence
    
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calculate optimal position size using Kelly Criterion"""
        if stop_loss == entry_price:
            return 0
        
        # Calculate win probability based on historical performance
        if len(self.trades_history) >= 20:
            win_rate = sum(1 for trade in self.trades_history[-20:] if trade['pnl'] > 0) / 20
            avg_win = np.mean([trade['pnl'] for trade in self.trades_history[-20:] if trade['pnl'] > 0])
            avg_loss = abs(np.mean([trade['pnl'] for trade in self.trades_history[-20:] if trade['pnl'] < 0]))
            
            if avg_loss > 0 and avg_win > 0:
                # Kelly Criterion: f = (bp - q) / b
                b = avg_win / avg_loss
                kelly_fraction = (b * win_rate - (1 - win_rate)) / b
                kelly_fraction = max(0, min(kelly_fraction, 0.2))  # Cap at 20%
            else:
                kelly_fraction = 0.1  # Default to 10%
        else:
            kelly_fraction = 0.1
        
        # Calculate position size
        risk_amount = self.equity * self.risk_per_trade * kelly_fraction
        risk_per_unit = abs(entry_price - stop_loss)
        
        if risk_per_unit > 0:
            position_size = risk_amount / risk_per_unit
            return max(0, position_size)
        
        return 0
    
    def check_risk_limits(self) -> bool:
        """Check if we should continue trading based on risk limits"""
        # Check drawdown limit
        current_drawdown = (self.max_equity - self.equity) / self.max_equity
        if current_drawdown > self.max_drawdown:
            logger.warning(f"Maximum drawdown limit reached: {current_drawdown:.2%}")
            return False
        
        # Check consecutive loss limit
        if self.consecutive_losses >= self.consecutive_loss_limit:
            logger.warning(f"Consecutive loss limit reached: {self.consecutive_losses}")
            return False
        
        return True
    
    def _record_trade(self, entry_price: float, exit_price: float, is_long: bool, is_take_profit: bool):
        """Record trade results for performance tracking"""
        if is_long:
            pnl = (exit_price - entry_price) / entry_price
        else:
            pnl = (entry_price - exit_price) / entry_price
        
        trade_record = {
            'entry_price': entry_price,
            'exit_price': exit_price,
            'is_long': is_long,
            'is_take_profit': is_take_profit,
            'pnl': pnl,
            'timestamp': len(self.data)
        }
        
        self.trades_history.append(trade_record)
        
        # Update consecutive losses counter
        if pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Log performance metrics
        if len(self.trades_history) % 10 == 0:
            self._log_performance_metrics()
    
    def _log_performance_metrics(self):
        """Log current performance metrics"""
        if len(self.trades_history) < 5:
            return
        
        recent_trades = self.trades_history[-self.performance_window:]
        win_rate = sum(1 for trade in recent_trades if trade['pnl'] > 0) / len(recent_trades)
        avg_win = np.mean([trade['pnl'] for trade in recent_trades if trade['pnl'] > 0]) if any(trade['pnl'] > 0 for trade in recent_trades) else 0
        avg_loss = np.mean([trade['pnl'] for trade in recent_trades if trade['pnl'] < 0]) if any(trade['pnl'] < 0 for trade in recent_trades) else 0
        profit_factor = abs(avg_win / avg_loss) if avg_loss != 0 else 0
        
        logger.info(f"Performance Metrics - "
                   f"Win Rate: {win_rate:.2%}, "
                   f"Avg Win: {avg_win:.2%}, "
                   f"Avg Loss: {avg_loss:.2%}, "
                   f"Profit Factor: {profit_factor:.2f}, "
                   f"Consecutive Losses: {self.consecutive_losses}")
    
    def next(self):
        """Main strategy logic"""
        try:
            # Update max equity
            if self.equity > self.max_equity:
                self.max_equity = self.equity
            
            # Check risk limits
            if not self.check_risk_limits():
                return
            
            # Skip if not enough data
            if len(self.data) < max(self.bb_period, self.rsi_period, self.ma_trend):
                return
            
            current_price = self.data.Close[-1]
            current_volume = self.data.Volume[-1]
            current_atr = self.atr[-1]
            
            # Calculate z-score and detect divergence
            z_score = self.calculate_z_score()
            bullish_divergence, bearish_divergence = self.detect_rsi_divergence()
            
            # Entry conditions
            if not self.position:
                # Long mean reversion entry (oversold conditions)
                long_conditions = (
                    z_score < -self.z_score_threshold and  # Price below mean
                    current_price <= self.bb_lower[-1] * 1.01 and  # Near lower Bollinger Band
                    self.rsi[-1] < self.rsi_oversold and  # RSI oversold
                    current_volume > (self.volume_ma[-1] * self.volume_threshold) and  # Volume confirmation
                    current_price > self.ma_trend_line[-1] and  # Above trend MA
                    bullish_divergence  # RSI divergence confirmation
                )
                
                if long_conditions:
                    # Calculate entry parameters
                    stop_loss = current_price - (current_atr * self.stop_loss_atr_multiplier)
                    take_profit = current_price + (current_atr * self.take_profit_atr_multiplier)
                    
                    # Calculate position size
                    position_size = self.calculate_position_size(current_price, stop_loss)
                    
                    if position_size > 0:
                        self.buy(size=position_size)
                        self.entry_prices[current_price] = current_price
                        self.stop_losses[current_price] = stop_loss
                        self.take_profits[current_price] = take_profit
                        
                        logger.info(f"Long mean reversion entry at {current_price:.4f} (z-score: {z_score:.2f}), SL: {stop_loss:.4f}, TP: {take_profit:.4f}")
                
                # Short mean reversion entry (overbought conditions)
                short_conditions = (
                    z_score > self.z_score_threshold and  # Price above mean
                    current_price >= self.bb_upper[-1] * 0.99 and  # Near upper Bollinger Band
                    self.rsi[-1] > self.rsi_overbought and  # RSI overbought
                    current_volume > (self.volume_ma[-1] * self.volume_threshold) and  # Volume confirmation
                    current_price < self.ma_trend_line[-1] and  # Below trend MA
                    bearish_divergence  # RSI divergence confirmation
                )
                
                if short_conditions:
                    # Calculate entry parameters
                    stop_loss = current_price + (current_atr * self.stop_loss_atr_multiplier)
                    take_profit = current_price - (current_atr * self.take_profit_atr_multiplier)
                    
                    # Calculate position size
                    position_size = self.calculate_position_size(current_price, stop_loss)
                    
                    if position_size > 0:
                        self.sell(size=position_size)
                        self.entry_prices[current_price] = current_price
                        self.stop_losses[current_price] = stop_loss
                        self.take_profits[current_price] = take_profit
                        
                        logger.info(f"Short mean reversion entry at {current_price:.4f} (z-score: {z_score:.2f}), SL: {stop_loss:.4f}, TP: {take_profit:.4f}")
            
            # Position management
            else:
                entry_price = self.position.entry_price
                if entry_price in self.stop_losses:
                    stop_loss = self.stop_losses[entry_price]
                    take_profit = self.take_profits[entry_price]
                    
                    if self.position.is_long:
                        # Check stop loss
                        if current_price <= stop_loss:
                            self.position.close()
                            self._record_trade(entry_price, current_price, True, False)
                            del self.entry_prices[entry_price]
                            del self.stop_losses[entry_price]
                            del self.take_profits[entry_price]
                            logger.info(f"Long position stopped out at {current_price:.4f}")
                            
                        # Check take profit
                        elif current_price >= take_profit:
                            self.position.close()
                            self._record_trade(entry_price, current_price, True, True)
                            del self.entry_prices[entry_price]
                            del self.stop_losses[entry_price]
                            del self.take_profits[entry_price]
                            logger.info(f"Long position take profit at {current_price:.4f}")
                            
                    elif self.position.is_short:
                        # Check stop loss
                        if current_price >= stop_loss:
                            self.position.close()
                            self._record_trade(entry_price, current_price, False, False)
                            del self.entry_prices[entry_price]
                            del self.stop_losses[entry_price]
                            del self.take_profits[entry_price]
                            logger.info(f"Short position stopped out at {current_price:.4f}")
                            
                        # Check take profit
                        elif current_price <= take_profit:
                            self.position.close()
                            self._record_trade(entry_price, current_price, False, True)
                            del self.entry_prices[entry_price]
                            del self.stop_losses[entry_price]
                            del self.take_profits[entry_price]
                            logger.info(f"Short position take profit at {current_price:.4f}")
        
        except Exception as e:
            logger.error(f"Error in next(): {str(e)}")
            raise

if __name__ == "__main__":
    # Example usage
    print("MeanReversionScalping strategy loaded successfully!")
    print("This strategy can be run through the backtesting engines.")
