#!/usr/bin/env python3
"""
XRP Momentum Rocket Strategy

Designed specifically for XRP's upcoming extreme bull run:
- Detects rocket-like momentum moves
- Uses multi-timeframe analysis for confirmation
- Implements aggressive position sizing for momentum
- Advanced risk management for extreme volatility
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

class XRPMomentumRocketStrategy(Strategy):
    """
    XRP Momentum Rocket Strategy
    
    Captures rocket-like momentum moves during XRP's extreme bull run:
    - Detects rocket-like momentum moves
    - Uses multi-timeframe analysis for confirmation
    - Implements aggressive position sizing for momentum
    - Advanced risk management for extreme volatility
    """
    
    # Core parameters - EXTREME BULL RUN
    risk_per_trade = 0.05          # 5% risk per trade (more aggressive)
    max_positions = 2              # Maximum concurrent positions
    max_drawdown = 0.15            # Maximum drawdown limit (15%)
    consecutive_loss_limit = 3     # Maximum consecutive losses
    
    # Momentum rocket parameters - EXTREME BULL RUN
    rocket_period = 3              # Period for rocket detection (faster)
    rocket_threshold = 0.02        # 2% move threshold for rocket (more sensitive)
    momentum_sustained = 2         # Periods for sustained momentum (faster)
    
    # Multi-timeframe parameters
    short_period = 5
    medium_period = 15
    long_period = 30
    
    # Momentum indicators
    rsi_period = 14
    rsi_oversold = 20
    rsi_overbought = 80
    
    # MACD parameters
    macd_fast = 5
    macd_slow = 13
    macd_signal = 3
    
    # Moving averages
    ema_fast = 8
    ema_medium = 21
    ema_slow = 55
    
    # Volatility
    atr_period = 14
    atr_multiplier = 1.2
    
    # XRP-specific parameters - EXTREME BULL RUN
    xrp_rocket_multiplier = 2.5    # XRP rocket patterns (higher multiplier)
    xrp_momentum_threshold = 0.3   # Lower momentum threshold for XRP (more sensitive)
    
    def init(self):
        """Initialize strategy indicators and tracking variables"""
        # Performance tracking
        self.trades_history = []
        self.consecutive_losses = 0
        self.max_equity = self.equity
        self.rocket_signals = []
        self.momentum_phases = []
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
        # Note: Custom indicators will be calculated in next() method
        
        # Bollinger Bands for volatility
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(
            talib.BBANDS, self.data.Close, timeperiod=20, nbdevup=2, nbdevdn=2
        )
        
        # Stochastic for momentum
        self.stoch_k, self.stoch_d = self.I(
            talib.STOCH, self.data.High, self.data.Low, self.data.Close,
            fastk_period=14, slowk_period=3, slowd_period=3
        )
        
        # Williams %R for momentum
        self.williams_r = self.I(talib.WILLR, self.data.High, self.data.Low, 
                                self.data.Close, timeperiod=14)
        
        # CCI for trend strength
        self.cci = self.I(talib.CCI, self.data.High, self.data.Low, 
                         self.data.Close, timeperiod=14)
        
        logger.info("XRP Momentum Rocket Strategy initialized successfully")
    
    def _calculate_rocket_momentum(self):
        """Calculate rocket momentum indicator"""
        if len(self.data) < self.rocket_period:
            return 0.0
        
        # Convert to pandas Series if needed
        close_prices = pd.Series(self.data.Close, index=self.data.index)
        
        # Calculate rate of change over rocket period
        roc = close_prices.pct_change(periods=self.rocket_period)
        
        # Apply XRP rocket multiplier
        rocket_momentum = roc * self.xrp_rocket_multiplier
        
        # Smooth the momentum using pandas rolling
        if len(rocket_momentum) >= 3:
            rocket_momentum = rocket_momentum.rolling(window=3).mean()
        else:
            rocket_momentum = rocket_momentum
        
        return rocket_momentum.fillna(0).iloc[-1]
    
    def _calculate_momentum_strength(self):
        """Calculate momentum strength indicator"""
        if len(self.data) < self.momentum_sustained:
            return 0.0
        
        # Convert to pandas Series if needed
        close_prices = pd.Series(self.data.Close, index=self.data.index)
        
        # Calculate momentum over sustained period
        momentum = close_prices.pct_change(periods=self.momentum_sustained)
        
        # Apply XRP momentum threshold
        momentum_strength = momentum / self.xrp_momentum_threshold
        
        return momentum_strength.fillna(0).iloc[-1]
    
    def _calculate_acceleration(self):
        """Calculate price acceleration indicator"""
        if len(self.data) < 5:
            return 0.0
        
        # Convert to pandas Series if needed
        close_prices = pd.Series(self.data.Close, index=self.data.index)
        
        # Calculate second derivative of price
        price_change = close_prices.pct_change()
        acceleration = price_change.diff()
        
        # Smooth the acceleration using pandas rolling
        if len(acceleration) >= 3:
            acceleration = acceleration.rolling(window=3).mean()
        else:
            acceleration = acceleration
        
        return acceleration.fillna(0).iloc[-1]
    
    def _calculate_volume_momentum(self):
        """Calculate volume momentum indicator"""
        if len(self.data) < 10:
            return 0.0
        
        # Convert to pandas Series if needed
        volume_data = pd.Series(self.data.Volume, index=self.data.index)
        
        # Volume momentum with better NaN handling
        volume_momentum = volume_data.pct_change(periods=10).fillna(0)
        
        # Smooth the momentum using pandas rolling
        if len(volume_momentum) >= 3:
            volume_momentum = volume_momentum.rolling(window=3).mean()
        else:
            volume_momentum = volume_momentum
        
        return volume_momentum.fillna(0).iloc[-1]
    
    def next(self):
        """Main strategy logic"""
        if len(self.data) < max(self.ema_slow, self.rocket_period * 2):
            return
        
        # Calculate custom indicators
        self.rocket_momentum = self._calculate_rocket_momentum()
        self.momentum_strength = self._calculate_momentum_strength()
        self.acceleration = self._calculate_acceleration()
        self.volume_momentum = self._calculate_volume_momentum()
        
        # Check for existing positions
        if self.position:
            self.manage_existing_positions()
        else:
            self.check_entry_signals()
    
    def check_entry_signals(self):
        """Check for entry signals"""
        # Rocket momentum signal
        if self.detect_rocket_momentum():
            self.enter_long_position()
        
        # Acceleration breakout
        elif self.detect_acceleration_breakout():
            self.enter_long_position()
    
    def detect_rocket_momentum(self) -> bool:
        """Detect rocket momentum pattern"""
        if len(self.data) < self.rocket_period + 5:
            return False
        
        # Rocket momentum
        rocket_momentum = self.rocket_momentum > self.rocket_threshold
        
        # Sustained momentum
        momentum_sustained = self.momentum_strength > 1.0
        
        # Price above all EMAs (strong uptrend)
        price_above_emas = (self.data.Close[-1] > self.ema_8[-1] and 
                           self.data.Close[-1] > self.ema_21[-1] and 
                           self.data.Close[-1] > self.ema_55[-1])
        
        # RSI momentum (not overbought)
        rsi_momentum = 30 < self.rsi[-1] < 75
        
        # MACD rocket
        macd_rocket = (self.macd[-1] > self.macd_signal_line[-1] and 
                      self.macd_histogram[-1] > 0 and
                      self.macd_histogram[-1] > self.macd_histogram[-2])
        
        # Acceleration positive
        acceleration_positive = self.acceleration > 0
        
        # Volume momentum
        volume_momentum = self.volume_momentum > 0.1
        
        # Stochastic rocket
        stoch_rocket = (self.stoch_k[-1] > self.stoch_d[-1] and 
                       self.stoch_k[-1] > 50)
        
        # Williams %R rocket
        williams_rocket = -30 < self.williams_r[-1] < 0
        
        # CCI strong
        cci_strong = self.cci[-1] > 100
        
        return (rocket_momentum and momentum_sustained and price_above_emas and 
                rsi_momentum and macd_rocket and acceleration_positive and 
                volume_momentum and stoch_rocket and williams_rocket and cci_strong)
    
    def detect_acceleration_breakout(self) -> bool:
        """Detect acceleration breakout pattern"""
        if len(self.data) < 10:
            return False
        
        # Strong acceleration
        acceleration_strong = self.acceleration > 0.02
        
        # Price breakout above Bollinger upper
        price_breakout = self.data.Close[-1] > self.bb_upper[-1]
        
        # Volume surge
        volume_surge = self.data.Volume[-1] > self.volume_ma[-1] * 1.5
        
        # RSI momentum
        rsi_momentum = 40 < self.rsi[-1] < 70
        
        # MACD acceleration
        macd_acceleration = (self.macd_histogram[-1] > self.macd_histogram[-2] and
                           self.macd_histogram[-1] > 0)
        
        # Stochastic acceleration
        stoch_acceleration = (self.stoch_k[-1] > self.stoch_d[-1] and 
                            self.stoch_k[-1] > self.stoch_k[-2])
        
        return (acceleration_strong and price_breakout and volume_surge and 
                rsi_momentum and macd_acceleration and stoch_acceleration)
    
    def enter_long_position(self):
        """Enter long position with rocket-based sizing"""
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
        """Calculate rocket-based position size for XRP - EXTREME BULL RUN"""
        # Base position size - more aggressive for $100k
        base_size = 0.50  # 50% of equity for XRP (more aggressive)
        
        # Rocket momentum multiplier
        rocket_multiplier = min(2.0, self.rocket_momentum / self.rocket_threshold)
        
        # Momentum strength multiplier
        momentum_multiplier = min(1.5, self.momentum_strength)
        
        # Acceleration multiplier
        acceleration_multiplier = min(1.3, max(1.0, self.acceleration * 50))
        
        # RSI momentum multiplier
        rsi_multiplier = 1.0
        if 50 < self.rsi[-1] < 70:
            rsi_multiplier = 1.3
        elif 30 < self.rsi[-1] < 50:
            rsi_multiplier = 1.1
        
        # Calculate final position size
        position_size = (base_size * rocket_multiplier * momentum_multiplier * 
                        acceleration_multiplier * rsi_multiplier)
        
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

        rocket_factor = min(3.0, self.rocket_momentum / self.rocket_threshold)
        take_profit_distance = stop_distance * rocket_factor * 3
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

        # Check for exit signals
        if self.should_exit_position():
            self.position.close()
            self._clear_manual_risk()
            logger.info("Exited position due to exit signal")
            return
        
        # Update stop loss (trailing stop)
        self.update_trailing_stop()
    
    def should_exit_position(self) -> bool:
        """Check if position should be exited"""
        # Rocket momentum weakening
        rocket_exit = (self.rocket_momentum < self.rocket_threshold * 0.3 and 
                      self.momentum_strength < 0.5)
        
        # Acceleration turning negative
        acceleration_exit = self.acceleration < -0.01
        
        # RSI overbought and momentum weakening
        rsi_exit = self.rsi[-1] > 85 and self.momentum_strength < 0.8
        
        # MACD bearish divergence
        macd_exit = (self.macd[-1] < self.macd_signal_line[-1] and 
                    self.macd_histogram[-1] < 0)
        
        # Price below EMA 8 (short-term trend weakening)
        trend_exit = self.data.Close[-1] < self.ema_8[-1]
        
        # Stochastic overbought
        stoch_exit = self.stoch_k[-1] > 85 and self.stoch_d[-1] > 85
        
        # CCI weakening
        cci_exit = self.cci[-1] < 50
        
        return (rocket_exit or acceleration_exit or rsi_exit or macd_exit or 
                trend_exit or stoch_exit or cci_exit)
    
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
