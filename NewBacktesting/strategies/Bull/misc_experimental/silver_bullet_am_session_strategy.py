#!/usr/bin/env python3
"""
Silver Bullet AM Session Strategy
Specialized strategy for morning trading sessions (Asian and European)
Based on the high-performing strategy from your results (28 backtests)
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from backtesting import Strategy
from datetime import datetime, time

class SilverBulletAMSessionStrategy(Strategy):
    """Silver Bullet AM Session Strategy for morning trading sessions"""
    
    def __init__(self):
        """Initialize the strategy with optimized parameters for AM sessions"""
        self.parameters = {
            # Core parameters
            'short_ma_period': 8,
            'long_ma_period': 21,
            'rsi_period': 14,
            'rsi_overbought': 75,
            'rsi_oversold': 25,
            
            # AM Session specific
            'am_start_hour': 6,  # 6 AM UTC (Asian session)
            'am_end_hour': 12,   # 12 PM UTC (European morning)
            'session_volume_threshold': 1.5,
            
            # Risk management
            'position_size': 0.15,
            'stop_loss': 0.03,  # 3% stop loss for AM sessions
            'take_profit': 0.08,  # 8% take profit
            'trailing_stop': 0.02,  # 2% trailing stop
            
            # Volatility filters
            'volatility_period': 20,
            'min_volatility': 0.01,
            'max_volatility': 0.05,
            
            # Momentum confirmation
            'momentum_period': 5,
            'momentum_threshold': 0.02,
            
            # Volume confirmation
            'volume_ma_period': 20,
            'volume_spike_threshold': 2.0
        }
    
    def is_am_session(self, timestamp) -> bool:
        """Check if current time is within AM session hours"""
        try:
            if hasattr(timestamp, 'hour'):
                hour = timestamp.hour
            else:
                hour = timestamp.hour if hasattr(timestamp, 'hour') else 0
            
            return self.parameters['am_start_hour'] <= hour < self.parameters['am_end_hour']
        except:
            return False
    
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate all required indicators"""
        df = data.copy()
        
        # Moving averages
        df['sma_short'] = df['Close'].rolling(window=self.parameters['short_ma_period']).mean()
        df['sma_long'] = df['Close'].rolling(window=self.parameters['long_ma_period']).mean()
        
        # RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.parameters['rsi_period']).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.parameters['rsi_period']).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Volatility (ATR)
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        df['atr'] = true_range.rolling(window=self.parameters['volatility_period']).mean()
        df['volatility'] = df['atr'] / df['Close']
        
        # Momentum
        df['momentum'] = df['Close'].pct_change(self.parameters['momentum_period'])
        
        # Volume indicators
        if 'Volume' in df.columns:
            df['volume_ma'] = df['Volume'].rolling(window=self.parameters['volume_ma_period']).mean()
            df['volume_ratio'] = df['Volume'] / df['volume_ma']
        else:
            df['volume_ratio'] = 1.0
        
        # AM Session filter
        df['is_am_session'] = df.index.map(self.is_am_session)
        
        # Signal strength calculation
        df['signal_strength'] = 0.0
        
        # MA crossover signal
        df['ma_signal'] = np.where(df['sma_short'] > df['sma_long'], 1, -1)
        
        # RSI signal
        df['rsi_signal'] = np.where(df['rsi'] < self.parameters['rsi_oversold'], 1,
                                   np.where(df['rsi'] > self.parameters['rsi_overbought'], -1, 0))
        
        # Momentum signal
        df['momentum_signal'] = np.where(df['momentum'] > self.parameters['momentum_threshold'], 1,
                                        np.where(df['momentum'] < -self.parameters['momentum_threshold'], -1, 0))
        
        # Volume signal
        df['volume_signal'] = np.where(df['volume_ratio'] > self.parameters['volume_spike_threshold'], 1, 0)
        
        return df
    
    def calculate_signals(self, data: pd.DataFrame) -> pd.Series:
        """Calculate trading signals from price data"""
        try:
            if len(data) < self.parameters['long_ma_period']:
                return pd.Series(0, index=data.index)
            
            df = self.calculate_indicators(data)
            signals = pd.Series(0, index=data.index)
            
            for i in range(len(df)):
                current = df.iloc[i]
                
                # Skip if not AM session
                if not current['is_am_session']:
                    continue
                
                # Skip if insufficient data
                if pd.isna(current['sma_short']) or pd.isna(current['rsi']):
                    continue
                
                # Calculate signal strength
                signal_strength = 0.0
                
                # MA Crossover (40% weight)
                if current['ma_signal'] == 1:
                    signal_strength += 0.4
                elif current['ma_signal'] == -1:
                    signal_strength -= 0.4
                
                # RSI (30% weight)
                if current['rsi_signal'] == 1:
                    signal_strength += 0.3
                elif current['rsi_signal'] == -1:
                    signal_strength -= 0.3
                
                # Momentum (20% weight)
                if current['momentum_signal'] == 1:
                    signal_strength += 0.2
                elif current['momentum_signal'] == -1:
                    signal_strength -= 0.2
                
                # Volume confirmation (10% weight)
                if current['volume_signal'] == 1:
                    signal_strength *= 1.1
                
                # Volatility filter
                if (current['volatility'] < self.parameters['min_volatility'] or 
                    current['volatility'] > self.parameters['max_volatility']):
                    signal_strength *= 0.5
                
                # Generate signals
                if signal_strength > 0.6:  # Strong buy signal
                    signals.iloc[i] = 1
                elif signal_strength < -0.6:  # Strong sell signal
                    signals.iloc[i] = -1
            
            return signals
            
        except Exception as e:
            return pd.Series(0, index=data.index)
    
    def init(self):
        """Initialize strategy indicators for backtesting.py"""
        # Calculate all indicators
        self.df = self.calculate_indicators(self.data)
        
        # Store key indicators
        self.sma_short = self.I(lambda: self.df['sma_short'])
        self.sma_long = self.I(lambda: self.df['sma_long'])
        self.rsi = self.I(lambda: self.df['rsi'])
        self.volatility = self.I(lambda: self.df['volatility'])
        self.momentum = self.I(lambda: self.df['momentum'])
        self.volume_ratio = self.I(lambda: self.df['volume_ratio'])
        self.is_am_session = self.I(lambda: self.df['is_am_session'])
        
        # Track entry price for trailing stop
        self.entry_price = None
        self.highest_price = None
        self.lowest_price = None
    
    def next(self):
        """Main strategy logic for backtesting.py"""
        # Only trade if we have enough data
        if len(self.data) < self.parameters['long_ma_period']:
            return
        
        # Skip if not AM session
        if not self.is_am_session[-1]:
            return
        
        current_price = self.data.Close[-1]
        current_sma_short = self.sma_short[-1]
        current_sma_long = self.sma_long[-1]
        current_rsi = self.rsi[-1]
        current_volatility = self.volatility[-1]
        current_momentum = self.momentum[-1]
        current_volume_ratio = self.volume_ratio[-1]
        
        # Skip if any indicator is NaN
        if (pd.isna(current_sma_short) or pd.isna(current_rsi) or 
            pd.isna(current_volatility) or pd.isna(current_momentum)):
            return
        
        # Volatility filter
        if (current_volatility < self.parameters['min_volatility'] or 
            current_volatility > self.parameters['max_volatility']):
            return
        
        # Entry conditions
        if not self.position:
            # Long entry: MA crossover + RSI oversold + positive momentum + volume
            if (current_sma_short > current_sma_long and
                current_rsi < self.parameters['rsi_oversold'] and
                current_momentum > self.parameters['momentum_threshold'] and
                current_volume_ratio > self.parameters['session_volume_threshold']):
                
                self.buy()
                self.entry_price = current_price
                self.highest_price = current_price
                self.lowest_price = current_price
            
            # Short entry: MA crossover + RSI overbought + negative momentum + volume
            elif (current_sma_short < current_sma_long and
                  current_rsi > self.parameters['rsi_overbought'] and
                  current_momentum < -self.parameters['momentum_threshold'] and
                  current_volume_ratio > self.parameters['session_volume_threshold']):
                
                self.sell()
                self.entry_price = current_price
                self.highest_price = current_price
                self.lowest_price = current_price
        
        # Exit conditions
        elif self.position:
            # Update highest/lowest prices
            if self.position.is_long:
                self.highest_price = max(self.highest_price, current_price)
            else:
                self.lowest_price = min(self.lowest_price, current_price)
            
            # Stop loss
            if self.position.is_long:
                stop_loss_price = self.entry_price * (1 - self.parameters['stop_loss'])
                if current_price <= stop_loss_price:
                    self.sell()
                    return
            else:
                stop_loss_price = self.entry_price * (1 + self.parameters['stop_loss'])
                if current_price >= stop_loss_price:
                    self.buy()
                    return
            
            # Take profit
            if self.position.is_long:
                take_profit_price = self.entry_price * (1 + self.parameters['take_profit'])
                if current_price >= take_profit_price:
                    self.sell()
                    return
            else:
                take_profit_price = self.entry_price * (1 - self.parameters['take_profit'])
                if current_price <= take_profit_price:
                    self.buy()
                    return
            
            # Trailing stop
            if self.position.is_long:
                trailing_stop_price = self.highest_price * (1 - self.parameters['trailing_stop'])
                if current_price <= trailing_stop_price:
                    self.sell()
                    return
            else:
                trailing_stop_price = self.lowest_price * (1 + self.parameters['trailing_stop'])
                if current_price >= trailing_stop_price:
                    self.buy()
                    return
            
            # RSI exit
            if self.position.is_long and current_rsi > self.parameters['rsi_overbought']:
                self.sell()
            elif self.position.is_short and current_rsi < self.parameters['rsi_oversold']:
                self.buy()
    
    def backtest(self, data: pd.DataFrame, initial_cash: float = 100000.0, commission: float = 0.001) -> Dict[str, Any]:
        """Run backtest on the strategy"""
        try:
            if data is None or len(data) == 0:
                return {
                    'total_return': 0.0,
                    'final_cash': initial_cash,
                    'trades_count': 0,
                    'error': 'Empty data'
                }
            
            # Calculate signals
            signals = self.calculate_signals(data)
            
            # Initialize variables
            cash = initial_cash
            position = 0
            trades = []
            equity_curve = []
            entry_price = None
            
            # Simulate trading
            for i in range(len(data)):
                current_price = data['Close'].iloc[i]
                signal = signals.iloc[i]
                
                # Calculate current equity
                current_equity = cash + (position * current_price)
                equity_curve.append(current_equity)
                
                # Execute trades based on signals
                if signal == 1 and position <= 0:  # Buy signal
                    if position < 0:
                        # Close short position
                        cash += abs(position) * current_price * (1 - commission)
                        trades.append({
                            'type': 'close_short',
                            'price': current_price,
                            'index': i
                        })
                    
                    # Open long position
                    position = int(cash * self.parameters['position_size'] / current_price)
                    if position > 0:
                        cash -= position * current_price * (1 + commission)
                        trades.append({
                            'type': 'buy',
                            'price': current_price,
                            'index': i
                        })
                        entry_price = current_price
                
                elif signal == -1 and position >= 0:  # Sell signal
                    if position > 0:
                        # Close long position
                        cash += position * current_price * (1 - commission)
                        trades.append({
                            'type': 'sell',
                            'price': current_price,
                            'index': i
                        })
                        position = 0
                        entry_price = None
                    
                    # Open short position
                    position = -int(cash * self.parameters['position_size'] / current_price)
                    if position < 0:
                        cash += abs(position) * current_price * (1 + commission)
                        trades.append({
                            'type': 'short',
                            'price': current_price,
                            'index': i
                        })
                        entry_price = current_price
            
            # Close final position
            final_price = data['Close'].iloc[-1]
            if position > 0:
                cash += position * final_price * (1 - commission)
            elif position < 0:
                cash -= abs(position) * final_price * (1 + commission)
            
            # Calculate returns
            total_return = (cash - initial_cash) / initial_cash
            
            return {
                'total_return': total_return,
                'final_cash': cash,
                'trades_count': len(trades),
                'equity_curve': equity_curve,
                'trades': trades
            }
            
        except Exception as e:
            return {
                'total_return': 0.0,
                'final_cash': initial_cash,
                'trades_count': 0,
                'error': str(e)
            }

# Strategy factory function
def create_strategy(parameters: Dict[str, Any] = None) -> SilverBulletAMSessionStrategy:
    """Create a strategy instance with given parameters"""
    strategy = SilverBulletAMSessionStrategy()
    if parameters:
        strategy.parameters.update(parameters)
    return strategy

# Default strategy parameters
DEFAULT_PARAMETERS = {
    'short_ma_period': 8,
    'long_ma_period': 21,
    'rsi_period': 14,
    'rsi_overbought': 75,
    'rsi_oversold': 25,
    'am_start_hour': 6,
    'am_end_hour': 12,
    'session_volume_threshold': 1.5,
    'position_size': 0.15,
    'stop_loss': 0.03,
    'take_profit': 0.08,
    'trailing_stop': 0.02,
    'volatility_period': 20,
    'min_volatility': 0.01,
    'max_volatility': 0.05,
    'momentum_period': 5,
    'momentum_threshold': 0.02,
    'volume_ma_period': 20,
    'volume_spike_threshold': 2.0
}
