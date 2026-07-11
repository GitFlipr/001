#!/usr/bin/env python3
"""
Enhanced Scalping Strategies Collection

This module contains several advanced scalping strategies that consolidate
multiple approaches into stronger, smarter strategies with:
- Advanced risk management
- Multi-indicator confirmation
- Adaptive parameters
- Performance tracking
- Market regime detection
"""

import pandas as pd
import numpy as np
import talib
import logging
from datetime import datetime
from backtesting import Backtest, Strategy
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EnhancedScalpingBase(Strategy):
    """
    Base class for enhanced scalping strategies with common functionality
    """
    
    # Common parameters for all scalping strategies
    risk_per_trade = 0.01          # 1% risk per trade
    max_positions = 2              # Maximum concurrent positions
    max_drawdown = 0.10            # Maximum drawdown limit (10%)
    consecutive_loss_limit = 4      # Maximum consecutive losses
    
    # Performance tracking
    track_performance = True
    performance_window = 50         # Performance calculation window
    
    def init(self):
        """Initialize common indicators and tracking variables"""
        # Performance tracking
        self.trades_history = []
        self.consecutive_losses = 0
        self.max_equity = self.equity
        self.entry_prices = {}
        self.stop_losses = {}
        self.take_profits = {}
        
        # Common indicators
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, 
                         self.data.Close, timeperiod=14)
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        
        logger.info(f"{self.__class__.__name__} initialized successfully")
    
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

class MultiIndicatorScalping(EnhancedScalpingBase):
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
    
    def init(self):
        """Initialize strategy indicators"""
        super().init()
        
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

class FibonacciScalping(EnhancedScalpingBase):
    """
    Fibonacci Retracement Scalping Strategy
    
    Uses Fibonacci retracement levels for precise entry and exit points:
    - Identifies swing highs and lows
    - Calculates Fibonacci retracement levels
    - Combines with RSI and volume confirmation
    - Dynamic stop loss based on Fibonacci levels
    """
    
    # Strategy parameters
    swing_period = 20              # Period for swing high/low calculation
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70
    
    fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]
    
    volume_threshold = 1.1
    atr_period = 14
    stop_loss_atr_multiplier = 1.5
    
    def init(self):
        """Initialize strategy indicators"""
        super().init()
        
        # RSI
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        
        # Additional indicators
        self.ema_20 = self.I(talib.EMA, self.data.Close, timeperiod=20)
        self.ema_50 = self.I(talib.EMA, self.data.Close, timeperiod=50)
        
        # Fibonacci tracking
        self.swing_highs = []
        self.swing_lows = []
        self.current_fib_levels = {}
        
        logger.info("FibonacciScalping initialized successfully")
    
    def calculate_swing_points(self):
        """Calculate swing highs and lows"""
        if len(self.data) < self.swing_period:
            return
        
        # Calculate rolling max and min
        rolling_max = pd.Series(self.data.High).rolling(window=self.swing_period, center=True).max()
        rolling_min = pd.Series(self.data.Low).rolling(window=self.swing_period, center=True).min()
        
        # Identify swing points
        current_high = self.data.High[-1]
        current_low = self.data.Low[-1]
        
        # Update swing highs
        if current_high == rolling_max.iloc[-1]:
            self.swing_highs.append({
                'price': current_high,
                'index': len(self.data) - 1,
                'timestamp': len(self.data)
            })
        
        # Update swing lows
        if current_low == rolling_min.iloc[-1]:
            self.swing_lows.append({
                'price': current_low,
                'index': len(self.data) - 1,
                'timestamp': len(self.data)
            })
        
        # Keep only recent swing points
        max_swings = 10
        if len(self.swing_highs) > max_swings:
            self.swing_highs = self.swing_highs[-max_swings:]
        if len(self.swing_lows) > max_swings:
            self.swing_lows = self.swing_lows[-max_swings:]
    
    def calculate_fibonacci_levels(self, high_price: float, low_price: float) -> Dict[float, float]:
        """Calculate Fibonacci retracement levels"""
        diff = high_price - low_price
        levels = {}
        
        for fib in self.fib_levels:
            if fib <= 0.5:
                levels[fib] = high_price - (diff * fib)
            else:
                levels[fib] = low_price + (diff * (1 - fib))
        
        return levels
    
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
            if len(self.data) < max(self.rsi_period, self.swing_period, self.atr_period):
                return
            
            # Calculate swing points
            self.calculate_swing_points()
            
            current_price = self.data.Close[-1]
            current_volume = self.data.Volume[-1]
            current_atr = self.atr[-1]
            
            # Entry conditions
            if not self.position and len(self.swing_highs) >= 2 and len(self.swing_lows) >= 2:
                # Get recent swing points
                recent_high = max(self.swing_highs[-2:], key=lambda x: x['price'])
                recent_low = min(self.swing_lows[-2:], key=lambda x: x['price'])
                
                # Calculate Fibonacci levels
                fib_levels = self.calculate_fibonacci_levels(recent_high['price'], recent_low['price'])
                
                # Long entry at Fibonacci support levels
                if (self.rsi[-1] < self.rsi_oversold and 
                    current_price <= fib_levels[0.618] * 1.01 and  # Near 61.8% level
                    current_volume > (self.volume_ma[-1] * self.volume_threshold) and
                    current_price > self.ema_20[-1]):
                    
                    # Calculate entry parameters
                    stop_loss = current_price - (current_atr * self.stop_loss_atr_multiplier)
                    take_profit = current_price + (current_atr * 2.5)
                    
                    # Calculate position size
                    position_size = self.calculate_position_size(current_price, stop_loss)
                    
                    if position_size > 0:
                        self.buy(size=position_size)
                        self.entry_prices[current_price] = current_price
                        self.stop_losses[current_price] = stop_loss
                        self.take_profits[current_price] = take_profit
                        
                        logger.info(f"Long entry at {current_price:.4f} (Fib 61.8%), SL: {stop_loss:.4f}, TP: {take_profit:.4f}")
                
                # Short entry at Fibonacci resistance levels
                elif (self.rsi[-1] > self.rsi_overbought and 
                      current_price >= fib_levels[0.382] * 0.99 and  # Near 38.2% level
                      current_volume > (self.volume_ma[-1] * self.volume_threshold) and
                      current_price < self.ema_20[-1]):
                    
                    # Calculate entry parameters
                    stop_loss = current_price + (current_atr * self.stop_loss_atr_multiplier)
                    take_profit = current_price - (current_atr * 2.5)
                    
                    # Calculate position size
                    position_size = self.calculate_position_size(current_price, stop_loss)
                    
                    if position_size > 0:
                        self.sell(size=position_size)
                        self.entry_prices[current_price] = current_price
                        self.stop_losses[current_price] = stop_loss
                        self.take_profits[current_price] = take_profit
                        
                        logger.info(f"Short entry at {current_price:.4f} (Fib 38.2%), SL: {stop_loss:.4f}, TP: {take_profit:.4f}")
            
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

class VolatilityBreakoutScalping(EnhancedScalpingBase):
    """
    Volatility Breakout Scalping Strategy
    
    Identifies and trades volatility breakouts:
    - Bollinger Band breakouts
    - ATR-based volatility expansion
    - Volume confirmation
    - Dynamic position sizing based on volatility
    """
    
    # Strategy parameters
    bb_period = 20
    bb_std = 2.0
    
    atr_period = 14
    atr_multiplier = 1.5  # For volatility expansion detection
    
    volume_threshold = 1.3
    rsi_period = 14
    rsi_oversold = 25
    rsi_overbought = 75
    
    def init(self):
        """Initialize strategy indicators"""
        super().init()
        
        # Bollinger Bands
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, self.data.Close,
                                                             timeperiod=self.bb_period,
                                                             nbdevup=self.bb_std,
                                                             nbdevdn=self.bb_std,
                                                             matype=0)
        
        # RSI
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        
        # Additional indicators
        self.ema_20 = self.I(talib.EMA, self.data.Close, timeperiod=20)
        self.ema_50 = self.I(talib.EMA, self.data.Close, timeperiod=50)
        
        # Volatility tracking
        self.atr_ma = self.I(talib.SMA, self.atr, timeperiod=20)
        
        logger.info("VolatilityBreakoutScalping initialized successfully")
    
    def detect_volatility_expansion(self) -> bool:
        """Detect if volatility is expanding"""
        if len(self.data) < self.atr_period:
            return False
        
        current_atr = self.atr[-1]
        avg_atr = self.atr_ma[-1]
        
        # Volatility expansion when current ATR > average ATR * multiplier
        return current_atr > (avg_atr * self.atr_multiplier)
    
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
            if len(self.data) < max(self.bb_period, self.atr_period, self.rsi_period):
                return
            
            current_price = self.data.Close[-1]
            current_volume = self.data.Volume[-1]
            current_atr = self.atr[-1]
            
            # Check for volatility expansion
            volatility_expanding = self.detect_volatility_expansion()
            
            # Entry conditions
            if not self.position and volatility_expanding:
                # Long breakout entry
                bb_breakout_up = current_price > self.bb_upper[-1]
                volume_confirmed = current_volume > (self.volume_ma[-1] * self.volume_threshold)
                rsi_not_overbought = self.rsi[-1] < self.rsi_overbought
                trend_aligned = current_price > self.ema_20[-1] > self.ema_50[-1]
                
                if (bb_breakout_up and volume_confirmed and rsi_not_overbought and trend_aligned):
                    
                    # Calculate entry parameters
                    stop_loss = current_price - (current_atr * 2.0)
                    take_profit = current_price + (current_atr * 3.0)
                    
                    # Calculate position size
                    position_size = self.calculate_position_size(current_price, stop_loss)
                    
                    if position_size > 0:
                        self.buy(size=position_size)
                        self.entry_prices[current_price] = current_price
                        self.stop_losses[current_price] = stop_loss
                        self.take_profits[current_price] = take_profit
                        
                        logger.info(f"Long breakout entry at {current_price:.4f}, SL: {stop_loss:.4f}, TP: {take_profit:.4f}")
                
                # Short breakdown entry
                bb_breakout_down = current_price < self.bb_lower[-1]
                volume_confirmed_short = current_volume > (self.volume_ma[-1] * self.volume_threshold)
                rsi_not_oversold = self.rsi[-1] > self.rsi_oversold
                trend_aligned_short = current_price < self.ema_20[-1] < self.ema_50[-1]
                
                if (bb_breakout_down and volume_confirmed_short and rsi_not_oversold and trend_aligned_short):
                    
                    # Calculate entry parameters
                    stop_loss = current_price + (current_atr * 2.0)
                    take_profit = current_price - (current_atr * 3.0)
                    
                    # Calculate position size
                    position_size = self.calculate_position_size(current_price, stop_loss)
                    
                    if position_size > 0:
                        self.sell(size=position_size)
                        self.entry_prices[current_price] = current_price
                        self.stop_losses[current_price] = stop_loss
                        self.take_profits[current_price] = take_profit
                        
                        logger.info(f"Short breakdown entry at {current_price:.4f}, SL: {stop_loss:.4f}, TP: {take_profit:.4f}")
            
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

# Strategy registry for easy access
SCALPING_STRATEGIES = {
    'multi_indicator': MultiIndicatorScalping,
    'fibonacci': FibonacciScalping,
    'volatility_breakout': VolatilityBreakoutScalping
}

def get_strategy_class(strategy_name: str):
    """Get strategy class by name"""
    return SCALPING_STRATEGIES.get(strategy_name)

def list_available_strategies() -> List[str]:
    """List all available strategy names"""
    return list(SCALPING_STRATEGIES.keys())

def run_backtest(strategy_name: str, data: pd.DataFrame, cash: float = 10000, 
                commission: float = 0.001, **kwargs) -> Dict:
    """
    Run backtest for a specific scalping strategy
    
    Args:
        strategy_name: Name of the strategy to run
        data: OHLCV data
        cash: Initial cash amount
        commission: Commission rate
        **kwargs: Additional parameters for Backtest
        
    Returns:
        Dictionary containing backtest results
    """
    try:
        strategy_class = get_strategy_class(strategy_name)
        if not strategy_class:
            raise ValueError(f"Unknown strategy: {strategy_name}")
        
        # Create backtest instance
        bt = Backtest(data, strategy_class, cash=cash, commission=commission, **kwargs)
        
        # Run backtest
        results = bt.run()
        
        # Print results
        print(f"\nBacktest Results for {strategy_name}:")
        print(f"Total Return: {results['Return [%]']:.2f}%")
        print(f"Sharpe Ratio: {results['Sharpe Ratio']:.3f}")
        print(f"Max Drawdown: {results['Max. Drawdown [%]']:.2f}%")
        print(f"Win Rate: {results['Win Rate [%]']:.2f}%")
        print(f"Profit Factor: {results['Profit Factor']:.3f}")
        print(f"Total Trades: {results['# Trades']}")
        
        return results
        
    except Exception as e:
        print(f"Error running backtest: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage
    print("Enhanced Scalping Strategies Available:")
    for name in list_available_strategies():
        print(f"  - {name}")
    
    print("\nTo run a strategy:")
    print("  from enhanced_scalping_strategies import run_backtest")
    print("  results = run_backtest('multi_indicator', data)")
