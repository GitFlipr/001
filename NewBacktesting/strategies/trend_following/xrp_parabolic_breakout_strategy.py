#!/usr/bin/env python3
"""
XRP Parabolic Breakout Strategy

Designed specifically for XRP's upcoming extreme bull run:
- Detects parabolic price movements and breakouts
- Uses volume surge analysis for confirmation
- Implements aggressive position sizing for parabolic moves
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

class XRPParabolicBreakoutStrategy(Strategy):
    """
    XRP Parabolic Breakout Strategy
    
    Captures parabolic price movements during XRP's extreme bull run:
    - Detects parabolic price patterns and breakouts
    - Uses volume surge analysis for confirmation
    - Implements aggressive position sizing for parabolic moves
    - Advanced risk management for extreme volatility
    """
    
    # Core parameters - EXTREME BULL RUN
    risk_per_trade = 0.04          # 4% risk per trade (more aggressive)
    max_positions = 2              # Maximum concurrent positions
    max_drawdown = 0.20            # Maximum drawdown limit (20%)
    consecutive_loss_limit = 3     # Maximum consecutive losses
    
    # Parabolic detection parameters - EXTREME BULL RUN
    parabolic_period = 10          # Period for parabolic detection (faster)
    parabolic_threshold = 0.05     # 5% move threshold for parabolic (more sensitive)
    breakout_threshold = 0.02      # 2% breakout threshold (more sensitive)
    
    # Volume analysis
    volume_period = 20
    volume_surge_threshold = 2.0   # 2x average volume for surge
    volume_breakout_threshold = 3.0 # 3x average volume for breakout
    
    # Momentum indicators
    rsi_period = 14
    rsi_oversold = 30
    rsi_overbought = 70
    
    # MACD parameters
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    
    # Moving averages
    ema_fast = 20
    ema_medium = 50
    ema_slow = 200
    
    # Volatility
    atr_period = 14
    atr_multiplier = 2.0
    
    # XRP-specific parameters
    xrp_volatility_multiplier = 1.5  # XRP is more volatile
    xrp_momentum_threshold = 0.8     # Higher momentum threshold for XRP
    
    def init(self):
        """Initialize strategy indicators and tracking variables"""
        # Performance tracking
        self.trades_history = []
        self.consecutive_losses = 0
        self.max_equity = self.equity
        self.parabolic_signals = []
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
        self.ema_20 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_fast)
        self.ema_50 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_medium)
        self.ema_200 = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_slow)
        
        # Volume analysis
        self.volume_ma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_period)
        
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
        
        # Parabolic indicators
        self.parabolic_sar = self.I(talib.SAR, self.data.High, self.data.Low)
        # Note: Custom indicators will be calculated in next() method
        
        logger.info("XRP Parabolic Breakout Strategy initialized successfully")
    
    def _calculate_parabolic_momentum(self):
        """Calculate parabolic momentum indicator"""
        if len(self.data) < self.parabolic_period:
            return 0.0
        
        # Convert to pandas Series if needed
        close_prices = pd.Series(self.data.Close, index=self.data.index)
        
        # Calculate rate of change over parabolic period
        roc = close_prices.pct_change(periods=self.parabolic_period)
        
        # Calculate momentum strength using pandas rolling
        if len(roc) >= 5:
            momentum = roc.rolling(window=5).mean()
        else:
            momentum = roc
        
        # Apply XRP volatility multiplier
        momentum = momentum * self.xrp_volatility_multiplier
        
        return momentum.fillna(0).iloc[-1]
    
    def _calculate_volume_surge(self):
        """Calculate volume surge indicator"""
        if len(self.data) < self.volume_period:
            return 0.0
        
        # Convert to pandas Series if needed
        volume_data = pd.Series(self.data.Volume, index=self.data.index)
        volume_ma_data = pd.Series(self.volume_ma, index=self.data.index)
        
        # Volume surge ratio
        volume_ratio = volume_data / volume_ma_data
        
        # Smooth the ratio using pandas rolling
        if len(volume_ratio) >= 3:
            volume_surge = volume_ratio.rolling(window=3).mean()
        else:
            volume_surge = volume_ratio
        
        return volume_surge.fillna(0).iloc[-1]
    
    def next(self):
        """Main strategy logic"""
        if len(self.data) < max(self.ema_slow, self.parabolic_period * 2):
            return
        
        # Calculate custom indicators
        self.parabolic_momentum = self._calculate_parabolic_momentum()
        self.volume_surge = self._calculate_volume_surge()
        
        # Check for existing positions
        if self.position:
            self.manage_existing_positions()
        else:
            self.check_entry_signals()
    
    def check_entry_signals(self):
        """Check for entry signals"""
        # Parabolic breakout signal
        if self.detect_parabolic_breakout():
            self.enter_long_position()
        
        # Volume surge breakout
        elif self.detect_volume_breakout():
            self.enter_long_position()
    
    def detect_parabolic_breakout(self) -> bool:
        """Detect parabolic breakout pattern"""
        if len(self.data) < self.parabolic_period + 5:
            return False
        
        # Price above all EMAs (strong uptrend)
        price_above_emas = (self.data.Close[-1] > self.ema_20[-1] and 
                           self.data.Close[-1] > self.ema_50[-1] and 
                           self.data.Close[-1] > self.ema_200[-1])
        
        # Parabolic momentum
        parabolic_momentum = self.parabolic_momentum > self.parabolic_threshold
        
        # Volume surge confirmation
        volume_surge = self.volume_surge > self.volume_surge_threshold
        
        # RSI not overbought (room to run)
        rsi_ok = 50 < self.rsi[-1] < 80
        
        # MACD bullish
        macd_bullish = (self.macd[-1] > self.macd_signal_line[-1] and 
                       self.macd_histogram[-1] > 0)
        
        # Stochastic bullish
        stoch_bullish = self.stoch_k[-1] > self.stoch_d[-1]
        
        # Williams %R bullish
        williams_bullish = -50 < self.williams_r[-1] < 0
        
        return (price_above_emas and parabolic_momentum and volume_surge and 
                rsi_ok and macd_bullish and stoch_bullish and williams_bullish)
    
    def detect_volume_breakout(self) -> bool:
        """Detect volume breakout pattern"""
        if len(self.data) < self.volume_period + 5:
            return False
        
        # Extreme volume surge
        volume_breakout = self.volume_surge > self.volume_breakout_threshold
        
        # Price breakout above resistance
        price_breakout = self.data.Close[-1] > self.bb_upper[-1]
        
        # Strong momentum
        momentum_strong = self.parabolic_momentum > self.xrp_momentum_threshold
        
        # RSI momentum
        rsi_momentum = self.rsi[-1] > 60
        
        return volume_breakout and price_breakout and momentum_strong and rsi_momentum
    
    def enter_long_position(self):
        """Enter long position with aggressive sizing"""
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
        """Calculate aggressive position size for XRP"""
        # Base position size - EXTREME BULL RUN
        base_size = 0.40  # 40% of equity for XRP (more aggressive)
        
        # Apply momentum multiplier
        momentum_multiplier = min(2.0, self.parabolic_momentum / self.parabolic_threshold)
        
        # Apply volume multiplier
        volume_multiplier = min(1.5, self.volume_surge / self.volume_surge_threshold)
        
        # Calculate final position size
        position_size = base_size * momentum_multiplier * volume_multiplier
        
        # Cap at maximum position size
        max_size = 0.5  # 50% maximum
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
        stop_distance = atr_value * self.atr_multiplier * self.xrp_volatility_multiplier
        stop_loss = entry_price - stop_distance

        momentum_factor = min(3.0, self.parabolic_momentum / self.parabolic_threshold)
        take_profit_distance = stop_distance * momentum_factor * 2
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
        # RSI overbought and momentum weakening
        rsi_exit = self.rsi[-1] > 85 and self.parabolic_momentum < self.parabolic_threshold * 0.5
        
        # Volume drying up
        volume_exit = self.volume_surge < 1.0
        
        # MACD bearish divergence
        macd_exit = (self.macd[-1] < self.macd_signal_line[-1] and 
                    self.macd_histogram[-1] < 0)
        
        # Price below EMA 20 (trend weakening)
        trend_exit = self.data.Close[-1] < self.ema_20[-1]
        
        return rsi_exit or volume_exit or macd_exit or trend_exit
    
    def update_trailing_stop(self):
        """Ratchet manual stop higher for longs."""
        if not self.position or not self.position.is_long or self._manual_sl is None:
            return

        current_price = self.data.Close[-1]

        atr_value = self.atr[-1]
        new_stop = current_price - (atr_value * self.atr_multiplier * self.xrp_volatility_multiplier)

        if self._manual_sl is not None and new_stop > self._manual_sl:
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
