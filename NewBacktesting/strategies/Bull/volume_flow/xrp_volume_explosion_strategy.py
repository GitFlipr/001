#!/usr/bin/env python3
"""
XRP Volume Explosion Strategy

Designed specifically for XRP's upcoming extreme bull run:
- Detects volume explosions and price breakouts
- Uses institutional flow analysis for XRP
- Implements momentum-based position sizing
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

class XRPVolumeExplosionStrategy(Strategy):
    """
    XRP Volume Explosion Strategy
    
    Captures volume explosions during XRP's extreme bull run:
    - Detects volume explosions and price breakouts
    - Uses institutional flow analysis for XRP
    - Implements momentum-based position sizing
    - Advanced risk management for extreme volatility
    """
    
    # Core parameters - EXTREME BULL RUN
    risk_per_trade = 0.04          # 4% risk per trade (more aggressive)
    max_positions = 2              # Maximum concurrent positions
    max_drawdown = 0.18            # Maximum drawdown limit (18%)
    consecutive_loss_limit = 3     # Maximum consecutive losses
    
    # Volume explosion parameters
    volume_explosion_threshold = 2.5   # 2.5x average volume
    volume_sustained_threshold = 1.8   # 1.8x average volume for sustained
    volume_period = 20
    
    # Price breakout parameters
    breakout_threshold = 0.03      # 3% breakout threshold
    resistance_lookback = 50       # Lookback for resistance levels
    
    # Momentum indicators
    rsi_period = 14
    rsi_oversold = 25
    rsi_overbought = 75
    
    # MACD parameters
    macd_fast = 8
    macd_slow = 21
    macd_signal = 5
    
    # Moving averages
    ema_fast = 12
    ema_medium = 26
    ema_slow = 50
    
    # Volatility
    atr_period = 14
    atr_multiplier = 1.5
    
    # XRP-specific parameters
    xrp_volume_multiplier = 1.2    # XRP volume patterns
    xrp_momentum_period = 8        # Shorter momentum period for XRP
    
    def init(self):
        """Initialize strategy indicators and tracking variables"""
        # Performance tracking
        self.trades_history = []
        self.consecutive_losses = 0
        self.max_equity = self.equity
        self.volume_explosions = []
        self.breakout_signals = []
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
        self.ema_12 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_fast)
        self.ema_26 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_medium)
        self.ema_50 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_slow)
        
        # Volume analysis
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_period)
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
        
        logger.info("XRP Volume Explosion Strategy initialized successfully")
    
    def _calculate_volume_explosion(self):
        """Calculate volume explosion indicator"""
        if len(self.data) < self.volume_period:
            return 0.0
        
        # Convert to pandas Series if needed
        volume_data = pd.Series(self.data.Volume, index=self.data.index)
        volume_ma_data = pd.Series(self.volume_ma, index=self.data.index)
        
        # Volume ratio with zero division protection
        volume_ratio = volume_data / volume_ma_data.replace(0, np.nan)
        volume_ratio = volume_ratio.fillna(1.0)  # Default to 1.0 if volume_ma is 0
        
        # Apply XRP volume multiplier
        volume_explosion = volume_ratio * self.xrp_volume_multiplier
        
        # Smooth the signal using pandas rolling
        if len(volume_explosion) >= 3:
            volume_explosion = volume_explosion.rolling(window=3).mean()
        else:
            volume_explosion = volume_explosion
        
        return volume_explosion.fillna(0).iloc[-1]
    
    def _calculate_volume_momentum(self):
        """Calculate volume momentum indicator"""
        if len(self.data) < self.xrp_momentum_period:
            return 0.0
        
        # Convert to pandas Series if needed
        volume_data = pd.Series(self.data.Volume, index=self.data.index)
        
        # Volume momentum (rate of change)
        volume_momentum = volume_data.pct_change(periods=self.xrp_momentum_period)
        
        # Smooth the momentum using pandas rolling
        if len(volume_momentum) >= 3:
            volume_momentum = volume_momentum.rolling(window=3).mean()
        else:
            volume_momentum = volume_momentum
        
        return volume_momentum.fillna(0).iloc[-1]
    
    def _calculate_higher_highs(self):
        """Calculate higher highs pattern"""
        if len(self.data) < 10:
            return False
        
        # Convert to pandas Series if needed
        high_data = pd.Series(self.data.High, index=self.data.index)
        
        # Look for higher highs over last 10 periods using pandas rolling
        if len(high_data) >= 10:
            highs = high_data.rolling(window=10).max()
            higher_highs = high_data > highs.shift(1)
        else:
            higher_highs = pd.Series([False] * len(high_data), index=high_data.index)
        
        return higher_highs.fillna(False).iloc[-1]
    
    def _calculate_breakout_signal(self):
        """Calculate breakout signal"""
        if len(self.data) < self.resistance_lookback:
            return False
        
        # Convert to pandas Series if needed
        high_data = pd.Series(self.data.High, index=self.data.index)
        close_data = pd.Series(self.data.Close, index=self.data.index)
        
        # Find recent resistance level using pandas rolling
        if len(high_data) >= self.resistance_lookback:
            resistance = high_data.rolling(window=self.resistance_lookback).max()
        else:
            resistance = high_data
        
        # Breakout signal
        breakout = close_data > resistance.shift(1) * (1 + self.breakout_threshold)
        
        return breakout.fillna(False).iloc[-1]
    
    def next(self):
        """Main strategy logic"""
        if len(self.data) < max(self.ema_slow, self.volume_period * 2):
            return
        
        # Calculate custom indicators
        self.volume_explosion = self._calculate_volume_explosion()
        self.volume_momentum = self._calculate_volume_momentum()
        self.higher_highs = self._calculate_higher_highs()
        self.breakout_signal = self._calculate_breakout_signal()
        
        # Check for existing positions
        if self.position:
            self.manage_existing_positions()
        else:
            self.check_entry_signals()
    
    def check_entry_signals(self):
        """Check for entry signals"""
        # Volume explosion signal
        if self.detect_volume_explosion():
            self.enter_long_position()
        
        # Breakout with volume confirmation
        elif self.detect_volume_breakout():
            self.enter_long_position()
    
    def detect_volume_explosion(self) -> bool:
        """Detect volume explosion pattern"""
        if len(self.data) < self.volume_period + 5:
            return False
        
        # Volume explosion
        volume_explosion = self.volume_explosion > self.volume_explosion_threshold
        
        # Sustained volume
        volume_sustained = self.volume_momentum > 0.1
        
        # Price above EMAs (uptrend)
        price_above_emas = (self.data.Close[-1] > self.ema_12[-1] and 
                           self.data.Close[-1] > self.ema_26[-1] and 
                           self.data.Close[-1] > self.ema_50[-1])
        
        # RSI momentum
        rsi_momentum = 40 < self.rsi[-1] < 70
        
        # MACD bullish
        macd_bullish = (self.macd[-1] > self.macd_signal_line[-1] and 
                       self.macd_histogram[-1] > 0)
        
        # Higher highs pattern
        higher_highs = self.higher_highs
        
        return (volume_explosion and volume_sustained and price_above_emas and 
                rsi_momentum and macd_bullish and higher_highs)
    
    def detect_volume_breakout(self) -> bool:
        """Detect volume breakout pattern"""
        if len(self.data) < self.resistance_lookback + 5:
            return False
        
        # Breakout signal
        breakout = self.breakout_signal
        
        # Volume confirmation
        volume_confirmation = self.volume_explosion > self.volume_sustained_threshold
        
        # Volume momentum
        volume_momentum = self.volume_momentum > 0.1
        
        # RSI not overbought
        rsi_ok = self.rsi[-1] < 75
        
        # Stochastic bullish
        stoch_bullish = self.stoch_k[-1] > self.stoch_d[-1]
        
        # Williams %R bullish
        williams_bullish = -50 < self.williams_r[-1] < 0
        
        return (breakout and volume_confirmation and volume_momentum and 
                rsi_ok and stoch_bullish and williams_bullish)
    
    def enter_long_position(self):
        """Enter long position with momentum-based sizing"""
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
        """Calculate momentum-based position size for XRP"""
        # Base position size - EXTREME BULL RUN
        base_size = 0.45  # 45% of equity for XRP (more aggressive)
        
        # Volume explosion multiplier
        volume_multiplier = min(1.5, self.volume_explosion / self.volume_explosion_threshold)
        
        # Momentum multiplier
        momentum_multiplier = min(1.3, abs(self.volume_momentum) * 10)
        
        # RSI momentum multiplier
        rsi_multiplier = 1.0
        if 50 < self.rsi[-1] < 70:
            rsi_multiplier = 1.2
        elif 30 < self.rsi[-1] < 50:
            rsi_multiplier = 1.0
        
        # Calculate final position size
        position_size = base_size * volume_multiplier * momentum_multiplier * rsi_multiplier
        
        # Cap at maximum position size
        max_size = 0.6  # 60% maximum
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

        volume_factor = min(2.0, self.volume_explosion / self.volume_explosion_threshold)
        take_profit_distance = stop_distance * volume_factor * 2.5
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
        # Volume drying up significantly
        volume_exit = self.volume_explosion < 0.8
        
        # RSI overbought and momentum weakening
        rsi_exit = self.rsi[-1] > 80 and self.volume_momentum < 0
        
        # MACD bearish divergence
        macd_exit = (self.macd[-1] < self.macd_signal_line[-1] and 
                    self.macd_histogram[-1] < 0)
        
        # Price below EMA 12 (short-term trend weakening)
        trend_exit = self.data.Close[-1] < self.ema_12[-1]
        
        # Stochastic overbought
        stoch_exit = self.stoch_k[-1] > 80 and self.stoch_d[-1] > 80
        
        return volume_exit or rsi_exit or macd_exit or trend_exit or stoch_exit
    
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
