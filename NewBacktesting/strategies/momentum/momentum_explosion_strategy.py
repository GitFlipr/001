#!/usr/bin/env python3
"""
Momentum Explosion Strategy

Designed for crypto momentum explosion trading:
- Detects momentum explosion patterns
- Uses acceleration and velocity analysis
- Implements explosion-based position sizing
- Risk management for explosion volatility
"""

import pandas as pd
import numpy as np
import talib
import logging
from backtesting import Strategy
from typing import Dict, List, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MomentumExplosionStrategy(Strategy):
    """
    Momentum Explosion Strategy
    
    Captures momentum explosion patterns in crypto markets:
    - Detects momentum explosion patterns
    - Uses acceleration and velocity analysis
    - Implements explosion-based position sizing
    - Risk management for explosion volatility
    """
    
    # Core parameters
    risk_per_trade = 0.03          # 3% risk per trade
    max_positions = 1              # Maximum concurrent positions
    max_drawdown = 0.15            # Maximum drawdown limit (15%)
    consecutive_loss_limit = 2     # Maximum consecutive losses
    
    # Explosion detection parameters
    explosion_period = 10          # Period for explosion detection
    explosion_threshold = 0.08     # 8% explosion threshold
    acceleration_period = 5        # Period for acceleration analysis
    
    # Moving averages
    ema_fast = 8
    ema_medium = 21
    ema_slow = 55
    
    # Momentum indicators
    rsi_period = 14
    rsi_oversold = 20
    rsi_overbought = 80
    
    # MACD parameters
    macd_fast = 5
    macd_slow = 13
    macd_signal = 3
    
    # Volatility
    atr_period = 14
    atr_multiplier = 1.2
    
    def init(self):
        """Initialize strategy indicators and tracking variables"""
        # Performance tracking
        self.trades_history = []
        self.consecutive_losses = 0
        self.max_equity = self.equity
        self.explosion_signals = []
        self._manual_sl = None
        self._manual_tp = None

        # Technical indicators
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, 
                         self.data.Close, timeperiod=self.atr_period)
        
        # MACD for momentum
        self.macd, self.macd_signal_line, self.macd_histogram = self.I(
            talib.MACD, self.data.Close, 
            fastperiod=self.macd_fast, 
            slowperiod=self.macd_slow, 
            signalperiod=self.macd_signal
        )
        
        # Moving averages
        self.ema_8 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_fast)
        self.ema_21 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_medium)
        self.ema_55 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_slow)
        
        # Volume analysis
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        
        # Bollinger Bands for volatility
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(
            talib.BBANDS, self.data.Close, timeperiod=20, nbdevup=2, nbdevdn=2
        )
        
        # Stochastic for momentum
        self.stoch_k, self.stoch_d = self.I(
            talib.STOCH, self.data.High, self.data.Low, self.data.Close,
            fastk_period=14, slowk_period=3, slowd_period=3
        )
        
        logger.info("Momentum Explosion Strategy initialized successfully")
    
    def _calculate_momentum_explosion(self):
        """Calculate momentum explosion indicator"""
        if len(self.data) < self.explosion_period:
            return 0.0
        
        # Convert to pandas Series if needed
        close_prices = pd.Series(self.data.Close, index=self.data.index)
        
        # Calculate rate of change over explosion period
        roc = close_prices.pct_change(periods=self.explosion_period)
        
        return roc.fillna(0).iloc[-1]
    
    def _calculate_acceleration(self):
        """Calculate acceleration indicator"""
        if len(self.data) < self.acceleration_period + 5:
            return 0.0
        
        # Convert to pandas Series if needed
        close_prices = pd.Series(self.data.Close, index=self.data.index)
        
        # Calculate first derivative (velocity)
        velocity = close_prices.pct_change()
        
        # Calculate second derivative (acceleration)
        acceleration = velocity.diff()
        
        # Smooth the acceleration
        if len(acceleration) >= 3:
            acceleration = acceleration.rolling(window=3).mean()
        else:
            acceleration = acceleration
        
        return acceleration.fillna(0).iloc[-1]
    
    def _calculate_volume_explosion(self):
        """Calculate volume explosion indicator"""
        if len(self.data) < 20:
            return 0.0
        
        # Convert to pandas Series if needed
        volume_data = pd.Series(self.data.Volume, index=self.data.index)
        volume_ma_data = pd.Series(self.volume_ma, index=self.data.index)
        
        # Volume explosion ratio
        volume_ratio = volume_data / volume_ma_data
        
        return volume_ratio.fillna(0).iloc[-1]
    
    def next(self):
        """Main strategy logic"""
        if len(self.data) < max(self.ema_slow, self.explosion_period):
            return
        
        # Calculate custom indicators
        self.momentum_explosion = self._calculate_momentum_explosion()
        self.acceleration = self._calculate_acceleration()
        self.volume_explosion = self._calculate_volume_explosion()
        
        # Check for existing positions
        if self.position:
            self.manage_existing_positions()
        else:
            self.check_entry_signals()
    
    def check_entry_signals(self):
        """Check for entry signals"""
        # Momentum explosion signal
        if self.detect_momentum_explosion():
            self.enter_long_position()
    
    def detect_momentum_explosion(self) -> bool:
        """Detect momentum explosion pattern"""
        if len(self.data) < self.explosion_period + 5:
            return False
        
        # Momentum explosion
        explosion_strong = self.momentum_explosion > self.explosion_threshold
        
        # Positive acceleration
        acceleration_positive = self.acceleration > 0.01
        
        # Volume explosion
        volume_explosion = self.volume_explosion > 1.5
        
        # Price above all EMAs (strong uptrend)
        price_above_emas = (self.data.Close[-1] > self.ema_8[-1] and 
                           self.data.Close[-1] > self.ema_21[-1] and 
                           self.data.Close[-1] > self.ema_55[-1])
        
        # RSI momentum (not overbought)
        rsi_momentum = 30 < self.rsi[-1] < 75
        
        # MACD explosion
        macd_explosion = (self.macd[-1] > self.macd_signal_line[-1] and 
                         self.macd_histogram[-1] > 0 and
                         self.macd_histogram[-1] > self.macd_histogram[-2])
        
        # Price breakout above Bollinger upper
        price_breakout = self.data.Close[-1] > self.bb_upper[-1]
        
        # Stochastic explosion
        stoch_explosion = (self.stoch_k[-1] > self.stoch_d[-1] and 
                          self.stoch_k[-1] > 50)
        
        return (explosion_strong and acceleration_positive and volume_explosion and 
                price_above_emas and rsi_momentum and macd_explosion and 
                price_breakout and stoch_explosion)
    
    def enter_long_position(self):
        """Enter long position with explosion-based sizing"""
        if self.consecutive_losses >= self.consecutive_loss_limit:
            return
        
        # Calculate position size
        position_size = self.calculate_position_size()
        
        if position_size > 0:
            # Enter long position
            self.buy(size=position_size)
            
            # Set stop loss and take profit
            self.set_stop_loss_and_take_profit()
            
            logger.info(f"Entered long position with size: {position_size}")
    
    def calculate_position_size(self) -> float:
        """Calculate explosion-based position size"""
        # Base position size
        base_size = 0.35  # 35% of equity
        
        # Explosion strength multiplier
        explosion_multiplier = min(2.0, self.momentum_explosion / self.explosion_threshold)
        
        # Acceleration multiplier
        acceleration_multiplier = min(1.5, max(1.0, self.acceleration * 100))
        
        # Volume explosion multiplier
        volume_multiplier = min(1.3, self.volume_explosion / 1.5)
        
        # RSI momentum multiplier
        rsi_multiplier = 1.0
        if 50 < self.rsi[-1] < 70:
            rsi_multiplier = 1.3
        elif 30 < self.rsi[-1] < 50:
            rsi_multiplier = 1.1
        
        # Calculate final position size
        position_size = (base_size * explosion_multiplier * acceleration_multiplier * 
                        volume_multiplier * rsi_multiplier)
        
        # Cap at maximum position size
        max_size = 0.7  # 70% maximum
        position_size = min(position_size, max_size)
        
        return position_size
    
    def _clear_manual_risk(self) -> None:
        self._manual_sl = None
        self._manual_tp = None

    def set_stop_loss_and_take_profit(self):
        """Track SL/TP in strategy state — backtesting ``Position`` has no writable stop fields."""
        if not self.position or not self.trades:
            return

        entry_price = float(self.trades[-1].entry_price)

        atr_value = self.atr[-1]
        stop_distance = atr_value * self.atr_multiplier
        stop_loss = entry_price - stop_distance

        explosion_factor = min(3.0, self.momentum_explosion / self.explosion_threshold)
        take_profit_distance = stop_distance * explosion_factor * 3
        take_profit = entry_price + take_profit_distance

        self._manual_sl = float(stop_loss)
        self._manual_tp = float(take_profit)

    def manage_existing_positions(self):
        """Manage existing positions"""
        if not self.position:
            return

        if self.position.is_long and self._manual_sl is not None:
            if float(self.data.Low[-1]) <= self._manual_sl:
                self.position.close()
                self._clear_manual_risk()
                logger.info("Exited long: stop loss")
                return
        if self.position.is_long and self._manual_tp is not None:
            if float(self.data.High[-1]) >= self._manual_tp:
                self.position.close()
                self._clear_manual_risk()
                logger.info("Exited long: take profit")
                return

        if self.should_exit_position():
            self.position.close()
            self._clear_manual_risk()
            logger.info("Exited position due to exit signal")
            return

        self.update_trailing_stop()
    
    def should_exit_position(self) -> bool:
        """Check if position should be exited"""
        # Explosion weakening
        explosion_weak = self.momentum_explosion < self.explosion_threshold * 0.3
        
        # Acceleration turning negative
        acceleration_negative = self.acceleration < -0.01
        
        # Volume drying up
        volume_weak = self.volume_explosion < 1.0
        
        # RSI overbought and momentum weakening
        rsi_exit = self.rsi[-1] > 85 and self.momentum_explosion < self.explosion_threshold * 0.5
        
        # MACD bearish divergence
        macd_exit = (self.macd[-1] < self.macd_signal_line[-1] and 
                    self.macd_histogram[-1] < 0)
        
        # Price below EMA 8 (short-term trend weakening)
        trend_exit = self.data.Close[-1] < self.ema_8[-1]
        
        # Stochastic overbought
        stoch_exit = self.stoch_k[-1] > 85 and self.stoch_d[-1] > 85
        
        return (explosion_weak or acceleration_negative or volume_weak or 
                rsi_exit or macd_exit or trend_exit or stoch_exit)
    
    def update_trailing_stop(self):
        """Ratchet manual stop higher for longs."""
        if not self.position or not self.position.is_long or self._manual_sl is None:
            return

        current_price = self.data.Close[-1]
        atr_value = self.atr[-1]
        new_stop = current_price - (atr_value * self.atr_multiplier)

        if new_stop > self._manual_sl:
            self._manual_sl = float(new_stop)
    
    def on_trade_closed(self, trade):
        """Handle trade closure"""
        self.trades_history.append({
            'entry_time': trade.entry_time,
            'exit_time': trade.exit_time,
            'pnl': trade.pnl,
            'pnl_pct': trade.pnl_pct
        })
        
        # Update consecutive losses
        if trade.pnl < 0:
            self.consecutive_losses += 1
        else:
            self.consecutive_losses = 0
        
        # Update max equity
        self.max_equity = max(self.max_equity, self.equity)
        
        logger.info(f"Trade closed: PnL: {trade.pnl:.2f}, PnL%: {trade.pnl_pct:.2f}%")
