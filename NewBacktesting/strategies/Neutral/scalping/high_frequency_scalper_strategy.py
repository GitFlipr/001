import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class HighFrequencyScalperStrategy:
    """
    High-Frequency Scalping Strategy for Maximum Profit
    
    Features:
    - Ultra-fast signal generation (1-5 minute timeframes)
    - Tight stop-losses (0.5-1%)
    - Quick profit-taking (1-2%)
    - Volume-based momentum detection
    - Micro-trend following
    - Aggressive position sizing
    - Maximum trade frequency
    """
    
    def __init__(self, name: str = "HighFrequencyScalper"):
        # Scalping parameters
        self.ema_fast = 5
        self.ema_slow = 10
        self.rsi_period = 7  # Shorter for faster signals
        self.rsi_oversold = 20
        self.rsi_overbought = 80
        
        # Aggressive risk management
        self.stop_loss_pct = 0.008  # 0.8% stop loss
        self.take_profit_pct = 0.015  # 1.5% take profit
        self.max_risk_per_trade = 0.03  # 3% per trade
        self.max_daily_trades = 50  # Maximum trades per day
        
        # Momentum parameters
        self.momentum_period = 3
        self.volume_threshold = 1.2
        self.price_acceleration_threshold = 0.005
        
        # Position sizing
        self.base_position_size = 0.02  # 2% base position
        self.momentum_multiplier = 3.0  # Triple position on strong momentum
        self.max_position_size = 0.06  # 6% maximum position
    
    def calculate_micro_momentum(self, data: pd.DataFrame) -> pd.Series:
        """Calculate micro-momentum for scalping."""
        close = data['Close']
        
        # Price acceleration (rate of change)
        price_change = close.pct_change()
        momentum = price_change.rolling(self.momentum_period).mean()
        
        # Volume momentum
        volume = data['Volume']
        volume_momentum = volume.pct_change().rolling(self.momentum_period).mean()
        
        # Combined micro-momentum
        micro_momentum = (momentum + volume_momentum) / 2
        
        return micro_momentum.fillna(0)
    
    def detect_micro_breakouts(self, data: pd.DataFrame) -> pd.Series:
        """Detect micro-breakouts for scalping entries."""
        close = data['Close']
        high = data['High']
        low = data['Low']
        
        # Calculate micro-resistance and support
        resistance = high.rolling(5).max()
        support = low.rolling(5).min()
        
        # Breakout detection
        breakout_up = close > resistance.shift(1)
        breakout_down = close < support.shift(1)
        
        # Volume confirmation
        volume = data['Volume']
        volume_ma = volume.rolling(10).mean()
        
        # Combined breakout signal
        breakout_signal = pd.Series(0, index=data.index)
        breakout_signal[breakout_up & (volume > volume_ma * self.volume_threshold)] = 1
        breakout_signal[breakout_down & (volume > volume_ma * self.volume_threshold)] = -1
        
        return breakout_signal
    
    def calculate_scalping_position_size(self, data: pd.DataFrame, current_price: float,
                                       momentum: float, volume_ratio: float) -> float:
        """Calculate aggressive position size for scalping."""
        
        # Base position size
        position_size = self.base_position_size
        
        # Momentum multiplier
        if abs(momentum) > self.price_acceleration_threshold:
            position_size *= self.momentum_multiplier
        
        # Volume multiplier
        if volume_ratio > 2.0:  # High volume
            position_size *= 1.5
        elif volume_ratio < 0.8:  # Low volume
            position_size *= 0.5
        
        # RSI-based adjustment
        rsi = self.calculate_rsi(data['Close'])
        current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
        
        if current_rsi < 20:  # Very oversold
            position_size *= 1.3
        elif current_rsi > 80:  # Very overbought
            position_size *= 0.7
        
        # Clamp to maximum
        position_size = min(position_size, self.max_position_size)
        
        return position_size
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """Calculate fast RSI for scalping."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi.fillna(50)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate high-frequency scalping signals."""
        signals = pd.Series(0, index=data.index)
        
        # Calculate indicators
        close = data['Close']
        ema_fast = close.ewm(span=self.ema_fast).mean()
        ema_slow = close.ewm(span=self.ema_slow).mean()
        rsi = self.calculate_rsi(close)
        micro_momentum = self.calculate_micro_momentum(data)
        breakout_signal = self.detect_micro_breakouts(data)
        
        # Initialize additional columns
        data['signal'] = 0
        data['stop_loss'] = 0.0
        data['take_profit'] = 0.0
        data['position_size'] = 0.0
        data['micro_momentum'] = micro_momentum
        data['breakout_signal'] = breakout_signal
        
        # Track daily trades
        daily_trades = 0
        last_trade_date = None
        
        # Generate scalping signals
        for i in range(1, len(data)):
            if i < 10:  # Skip initial periods
                continue
            
            current_price = close.iloc[i]
            current_ema_fast = ema_fast.iloc[i]
            current_ema_slow = ema_slow.iloc[i]
            current_rsi = rsi.iloc[i]
            current_momentum = micro_momentum.iloc[i]
            current_breakout = breakout_signal.iloc[i]
            
            # Check daily trade limit
            current_date = data.index[i] if hasattr(data.index[i], 'date') else pd.Timestamp(data.index[i]).date()
            if last_trade_date != current_date:
                daily_trades = 0
                last_trade_date = current_date
            
            if daily_trades >= self.max_daily_trades:
                continue
            
            # Volume ratio
            volume = data['Volume']
            volume_ma = volume.rolling(10).mean()
            volume_ratio = volume.iloc[i] / volume_ma.iloc[i] if volume_ma.iloc[i] > 0 else 1.0
            
            # Scalping buy conditions
            buy_conditions = (
                current_ema_fast > current_ema_slow and  # Fast EMA above slow EMA
                current_rsi < self.rsi_overbought and  # Not overbought
                current_momentum > self.price_acceleration_threshold and  # Positive momentum
                current_breakout == 1 and  # Upward breakout
                volume_ratio > self.volume_threshold  # Volume confirmation
            )
            
            # Scalping sell conditions
            sell_conditions = (
                current_ema_fast < current_ema_slow and  # Fast EMA below slow EMA
                current_rsi > self.rsi_oversold and  # Not oversold
                current_momentum < -self.price_acceleration_threshold and  # Negative momentum
                current_breakout == -1 and  # Downward breakout
                volume_ratio > self.volume_threshold  # Volume confirmation
            )
            
            if buy_conditions:
                signals.iloc[i] = 1
                data.iloc[i, data.columns.get_loc('signal')] = 1
                daily_trades += 1
                
                # Calculate aggressive position size
                position_size = self.calculate_scalping_position_size(
                    data.iloc[:i+1], current_price, current_momentum, volume_ratio
                )
                
                # Tight stop-loss and quick take-profit
                stop_loss = current_price * (1 - self.stop_loss_pct)
                take_profit = current_price * (1 + self.take_profit_pct)
                
                data.iloc[i, data.columns.get_loc('stop_loss')] = stop_loss
                data.iloc[i, data.columns.get_loc('take_profit')] = take_profit
                data.iloc[i, data.columns.get_loc('position_size')] = position_size
            
            elif sell_conditions:
                signals.iloc[i] = -1
                data.iloc[i, data.columns.get_loc('signal')] = -1
                daily_trades += 1
                
                # Calculate aggressive position size
                position_size = self.calculate_scalping_position_size(
                    data.iloc[:i+1], current_price, current_momentum, volume_ratio
                )
                
                # Tight stop-loss and quick take-profit
                stop_loss = current_price * (1 + self.stop_loss_pct)
                take_profit = current_price * (1 - self.take_profit_pct)
                
                data.iloc[i, data.columns.get_loc('stop_loss')] = stop_loss
                data.iloc[i, data.columns.get_loc('take_profit')] = take_profit
                data.iloc[i, data.columns.get_loc('position_size')] = position_size
        
        return data
    
    def get_parameters(self) -> dict:
        """Get strategy parameters for optimization."""
        return {
            'ema_fast': self.ema_fast,
            'ema_slow': self.ema_slow,
            'rsi_period': self.rsi_period,
            'rsi_oversold': self.rsi_oversold,
            'rsi_overbought': self.rsi_overbought,
            'stop_loss_pct': self.stop_loss_pct,
            'take_profit_pct': self.take_profit_pct,
            'max_risk_per_trade': self.max_risk_per_trade,
            'max_daily_trades': self.max_daily_trades,
            'momentum_period': self.momentum_period,
            'volume_threshold': self.volume_threshold,
            'price_acceleration_threshold': self.price_acceleration_threshold,
            'base_position_size': self.base_position_size,
            'momentum_multiplier': self.momentum_multiplier,
            'max_position_size': self.max_position_size
        } 