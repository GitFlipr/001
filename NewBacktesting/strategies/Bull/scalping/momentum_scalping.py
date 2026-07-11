#!/usr/bin/env python3
"""
Momentum Scalping Strategy

A high-frequency scalping strategy that capitalizes on strong momentum moves:
- RSI momentum confirmation
- MACD trend strength
- Volume surge detection
- Dynamic momentum thresholds
- Quick entry/exit for scalping
"""

import pandas as pd
import numpy as np
import talib
import logging
from backtesting import Strategy

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MomentumScalping(Strategy):
    """
    Momentum Scalping Strategy
    
    A high-frequency scalping strategy that capitalizes on strong momentum moves:
    - RSI momentum confirmation
    - MACD trend strength
    - Volume surge detection
    - Dynamic momentum thresholds
    - Quick entry/exit for scalping
    """
    
    # Strategy parameters
    risk_per_trade = 0.008         # 0.8% risk per trade (lower for scalping)
    max_positions = 3              # Maximum concurrent positions
    max_drawdown = 0.08            # Maximum drawdown limit (8%)
    consecutive_loss_limit = 5      # Maximum consecutive losses
    
    # Momentum parameters
    rsi_period = 14
    rsi_momentum_threshold = 60    # RSI threshold for momentum
    rsi_oversold = 25
    rsi_overbought = 75
    
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    macd_momentum_threshold = 0.0001  # Minimum MACD change for momentum
    
    # Volume parameters
    volume_surge_threshold = 1.5   # Volume must be 50% above average
    volume_ma_period = 20
    
    # ATR parameters
    atr_period = 14
    stop_loss_atr_multiplier = 1.5
    take_profit_atr_multiplier = 2.5
    
    # Momentum acceleration
    momentum_acceleration_period = 5
    price_change_threshold = 0.002  # 0.2% price change for momentum
    
    # Performance tracking
    track_performance = True
    performance_window = 30         # Performance calculation window (shorter for scalping)
    
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
        
        # RSI
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        
        # MACD
        self.macd, self.macd_signal, self.macd_hist = self.I(talib.MACD, self.data.Close,
                                                           fastperiod=self.macd_fast,
                                                           slowperiod=self.macd_slow,
                                                           signalperiod=self.macd_signal)
        
        # Moving averages for trend
        self.ema_10 = self.I(talib.EMA, self.data.Close, timeperiod=10)
        self.ema_20 = self.I(talib.EMA, self.data.Close, timeperiod=20)
        
        # Momentum indicators
        self.momentum = self.I(talib.MOM, self.data.Close, timeperiod=self.momentum_acceleration_period)
        self.roc = self.I(talib.ROC, self.data.Close, timeperiod=10)
        
        logger.info("MomentumScalping initialized successfully")
    
    def detect_momentum_surge(self) -> tuple[bool, bool]:
        """
        Detect momentum surge for both long and short opportunities
        
        Returns:
            tuple: (long_momentum, short_momentum)
        """
        if len(self.data) < max(self.rsi_period, self.macd_slow, self.momentum_acceleration_period):
            return False, False
        
        current_price = self.data.Close[-1]
        prev_price = self.data.Close[-2]
        
        # Price momentum
        price_change = (current_price - prev_price) / prev_price
        price_momentum_up = price_change > self.price_change_threshold
        price_momentum_down = price_change < -self.price_change_threshold
        
        # RSI momentum
        rsi_current = self.rsi[-1]
        rsi_prev = self.rsi[-2]
        rsi_momentum_up = rsi_current > self.rsi_momentum_threshold and rsi_current > rsi_prev
        rsi_momentum_down = rsi_current < (100 - self.rsi_momentum_threshold) and rsi_current < rsi_prev
        
        # MACD momentum
        macd_current = self.macd[-1]
        macd_prev = self.macd[-2]
        macd_momentum_up = (macd_current > macd_prev and 
                           abs(macd_current - macd_prev) > self.macd_momentum_threshold)
        macd_momentum_down = (macd_current < macd_prev and 
                             abs(macd_current - macd_prev) > self.macd_momentum_threshold)
        
        # Volume confirmation
        current_volume = self.data.Volume[-1]
        volume_surge = current_volume > (self.volume_ma[-1] * self.volume_surge_threshold)
        
        # Combined momentum signals
        long_momentum = (price_momentum_up and rsi_momentum_up and 
                        macd_momentum_up and volume_surge)
        short_momentum = (price_momentum_down and rsi_momentum_down and 
                         macd_momentum_down and volume_surge)
        
        return long_momentum, short_momentum
    
    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """Calculate optimal position size using Kelly Criterion"""
        if stop_loss == entry_price:
            return 0
        
        # Calculate win probability based on historical performance
        if len(self.trades_history) >= 15:  # Shorter window for scalping
            win_rate = sum(1 for trade in self.trades_history[-15:] if trade['pnl'] > 0) / 15
            avg_win = np.mean([trade['pnl'] for trade in self.trades_history[-15:] if trade['pnl'] > 0])
            avg_loss = abs(np.mean([trade['pnl'] for trade in self.trades_history[-15:] if trade['pnl'] < 0]))
            
            if avg_loss > 0 and avg_win > 0:
                # Kelly Criterion: f = (bp - q) / b
                b = avg_win / avg_loss
                kelly_fraction = (b * win_rate - (1 - win_rate)) / b
                kelly_fraction = max(0, min(kelly_fraction, 0.15))  # Cap at 15% for scalping
            else:
                kelly_fraction = 0.08  # Default to 8% for scalping
        else:
            kelly_fraction = 0.08
        
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
        if len(self.trades_history) % 5 == 0:  # More frequent logging for scalping
            self._log_performance_metrics()
    
    def _log_performance_metrics(self):
        """Log current performance metrics"""
        if len(self.trades_history) < 3:
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
            if len(self.data) < max(self.rsi_period, self.macd_slow, self.momentum_acceleration_period):
                return
            
            current_price = self.data.Close[-1]
            current_atr = self.atr[-1]
            
            # Detect momentum surge
            long_momentum, short_momentum = self.detect_momentum_surge()
            
            # Entry conditions
            if not self.position:
                # Long momentum entry
                if long_momentum:
                    # Additional trend confirmation
                    trend_aligned = (current_price > self.ema_10[-1] > self.ema_20[-1] and
                                   self.ema_10[-1] > self.ema_10[-2])
                    
                    if trend_aligned:
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
                            
                            logger.info(f"Long momentum entry at {current_price:.4f}, SL: {stop_loss:.4f}, TP: {take_profit:.4f}")
                
                # Short momentum entry
                elif short_momentum:
                    # Additional trend confirmation
                    trend_aligned = (current_price < self.ema_10[-1] < self.ema_20[-1] and
                                   self.ema_10[-1] < self.ema_10[-2])
                    
                    if trend_aligned:
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
                            
                            logger.info(f"Short momentum entry at {current_price:.4f}, SL: {stop_loss:.4f}, TP: {take_profit:.4f}")
            
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
    print("MomentumScalping strategy loaded successfully!")
    print("This strategy can be run through the backtesting engines.")
