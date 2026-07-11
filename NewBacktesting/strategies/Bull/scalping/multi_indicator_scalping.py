#!/usr/bin/env python3
"""
Multi-Indicator Scalping Strategy

A high-probability scalping strategy that combines multiple technical indicators:
- RSI for momentum
- MACD for trend confirmation
- Bollinger Bands for volatility
- Volume confirmation
- ATR for dynamic stops
"""

import pandas as pd
import numpy as np
import talib
import logging
from backtesting import Strategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MultiIndicatorScalping(Strategy):
    """
    Multi-Indicator Scalping Strategy
    
    Combines multiple technical indicators for high-probability scalping:
    - RSI for momentum
    - MACD for trend confirmation
    - Bollinger Bands for volatility
    - Volume confirmation
    - ATR for dynamic stops
    """
    
    # Strategy parameters
    risk_per_trade = 0.01          # 1% risk per trade
    max_positions = 2              # Maximum concurrent positions
    max_drawdown = 0.10            # Maximum drawdown limit (10%)
    consecutive_loss_limit = 4      # Maximum consecutive losses
    
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70
    
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    
    bb_period = 20
    bb_std = 2.0
    
    atr_period = 14
    stop_loss_atr_multiplier = 2.0
    take_profit_atr_multiplier = 3.0
    
    volume_threshold = 1.2  # Volume must be 20% above average
    
    # Performance tracking
    track_performance = True
    performance_window = 50         # Performance calculation window
    
    def init(self):
        """Initialize strategy indicators and tracking variables"""
        # Performance tracking
        self.trades_history = []
        self.consecutive_losses = 0
        self.max_equity = self.equity
        self.entry_prices = {}
        self.stop_losses = {}
        self.take_profits = {}
        
        # Common indicators
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, 
                         self.data.Close, timeperiod=self.atr_period)
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        
        # RSI
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        
        # MACD
        self.macd, self.macd_signal, self.macd_hist = self.I(talib.MACD, self.data.Close,
                                                            fastperiod=self.macd_fast,
                                                            slowperiod=self.macd_slow,
                                                            signalperiod=self.macd_signal)
        
        # Bollinger Bands
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, self.data.Close,
                                                             timeperiod=self.bb_period,
                                                             nbdevup=self.bb_std,
                                                             nbdevdn=self.bb_std,
                                                             matype=0)
        
        # Additional indicators
        self.ema_20 = self.I(talib.EMA, self.data.Close, timeperiod=20)
        self.ema_50 = self.I(talib.EMA, self.data.Close, timeperiod=50)
        
        logger.info("MultiIndicatorScalping initialized successfully")
    
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
            if len(self.data) < max(self.rsi_period, self.macd_slow, self.bb_period, self.atr_period):
                return
            
            current_price = self.data.Close[-1]
            current_volume = self.data.Volume[-1]
            current_atr = self.atr[-1]
            
            # Calculate dynamic stop loss and take profit
            stop_loss_distance = current_atr * self.stop_loss_atr_multiplier
            take_profit_distance = current_atr * self.take_profit_atr_multiplier
            
            # Entry conditions
            if not self.position:
                # Long entry conditions
                rsi_oversold = self.rsi[-1] < self.rsi_oversold
                macd_bullish = self.macd[-1] > self.macd_signal[-1]
                price_near_lower_bb = current_price <= self.bb_lower[-1] * 1.01
                volume_confirmed = current_volume > (self.volume_ma[-1] * self.volume_threshold)
                trend_aligned = current_price > self.ema_20[-1] > self.ema_50[-1]
                
                if (rsi_oversold and macd_bullish and price_near_lower_bb and 
                    volume_confirmed and trend_aligned):
                    
                    # Calculate entry parameters
                    stop_loss = current_price - stop_loss_distance
                    take_profit = current_price + take_profit_distance
                    
                    # Calculate position size
                    position_size = self.calculate_position_size(current_price, stop_loss)
                    
                    if position_size > 0:
                        self.buy(size=position_size)
                        self.entry_prices[current_price] = current_price
                        self.stop_losses[current_price] = stop_loss
                        self.take_profits[current_price] = take_profit
                        
                        logger.info(f"Long entry at {current_price:.4f}, SL: {stop_loss:.4f}, TP: {take_profit:.4f}")
                
                # Short entry conditions
                rsi_overbought = self.rsi[-1] > self.rsi_overbought
                macd_bearish = self.macd[-1] < self.macd_signal[-1]
                price_near_upper_bb = current_price >= self.bb_upper[-1] * 0.99
                volume_confirmed_short = current_volume > (self.volume_ma[-1] * self.volume_threshold)
                trend_aligned_short = current_price < self.ema_20[-1] < self.ema_50[-1]
                
                if (rsi_overbought and macd_bearish and price_near_upper_bb and 
                    volume_confirmed_short and trend_aligned_short):
                    
                    # Calculate entry parameters
                    stop_loss = current_price + stop_loss_distance
                    take_profit = current_price - take_profit_distance
                    
                    # Calculate position size
                    position_size = self.calculate_position_size(current_price, stop_loss)
                    
                    if position_size > 0:
                        self.sell(size=position_size)
                        self.entry_prices[current_price] = current_price
                        self.stop_losses[current_price] = stop_loss
                        self.take_profits[current_price] = take_profit
                        
                        logger.info(f"Short entry at {current_price:.4f}, SL: {stop_loss:.4f}, TP: {take_profit:.4f}")
            
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
    print("MultiIndicatorScalping strategy loaded successfully!")
    print("This strategy can be run through the backtesting engines.")
