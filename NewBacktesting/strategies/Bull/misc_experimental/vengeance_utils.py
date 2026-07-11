import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Trade:
    """Represents a single trade with its details"""
    entry_time: datetime
    exit_time: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    position_size: float
    direction: str  # 'long' or 'short'
    pnl: Optional[float]
    max_drawdown: float
    holding_period: Optional[float]  # in days

class TradeAnalyzer:
    """Analyzes trade data and generates insights"""
    
    @staticmethod
    def analyze_trades(trades: List[Trade]) -> Dict:
        """Analyze a list of trades and return statistics"""
        if not trades:
            return {}
            
        # Calculate basic statistics
        winning_trades = [t for t in trades if t.pnl and t.pnl > 0]
        losing_trades = [t for t in trades if t.pnl and t.pnl <= 0]
        
        total_pnl = sum(t.pnl for t in trades if t.pnl)
        win_rate = len(winning_trades) / len(trades)
        
        # Calculate average win/loss
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t.pnl for t in losing_trades]) if losing_trades else 0
        
        # Calculate risk metrics
        max_drawdown = max(t.max_drawdown for t in trades)
        avg_holding_period = np.mean([t.holding_period for t in trades if t.holding_period])
        
        return {
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': abs(avg_win / avg_loss) if avg_loss != 0 else float('inf'),
            'max_drawdown': max_drawdown,
            'avg_holding_period': avg_holding_period
        }
    
    @staticmethod
    def generate_trade_signals(data: pd.DataFrame,
                             entry_threshold: float = 0.02,
                             exit_threshold: float = 0.01) -> Tuple[pd.Series, pd.Series]:
        """
        Generate entry and exit signals based on price action.
        
        Args:
            data: OHLCV data
            entry_threshold: Price movement threshold for entry
            exit_threshold: Price movement threshold for exit
            
        Returns:
            Tuple of entry and exit signals
        """
        # Calculate price changes
        price_changes = data['Close'].pct_change()
        
        # Generate entry signals
        entry_signals = pd.Series(False, index=data.index)
        entry_signals[price_changes > entry_threshold] = True
        
        # Generate exit signals
        exit_signals = pd.Series(False, index=data.index)
        exit_signals[abs(price_changes) > exit_threshold] = True
        
        return entry_signals, exit_signals

class DataPreprocessor:
    """Handles data preprocessing and cleaning"""
    
    @staticmethod
    def clean_data(data: pd.DataFrame) -> pd.DataFrame:
        """Clean and prepare data for analysis"""
        # Clean column names
        data.columns = data.columns.str.strip().str.lower()
        
        # Drop unnamed columns
        data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
        
        # Ensure required columns exist
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in data.columns for col in required_columns):
            raise ValueError(f"Missing required columns: {required_columns}")
        
        # Convert datetime
        if 'datetime' in data.columns:
            data['datetime'] = pd.to_datetime(data['datetime'])
            data = data.set_index('datetime')
        
        return data
    
    @staticmethod
    def add_technical_indicators(data: pd.DataFrame) -> pd.DataFrame:
        """Add common technical indicators to the data"""
        # Calculate moving averages
        data['sma_20'] = data['close'].rolling(window=20).mean()
        data['sma_50'] = data['close'].rolling(window=50).mean()
        data['sma_200'] = data['close'].rolling(window=200).mean()
        
        # Calculate RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))
        
        # Calculate MACD
        exp1 = data['close'].ewm(span=12, adjust=False).mean()
        exp2 = data['close'].ewm(span=26, adjust=False).mean()
        data['macd'] = exp1 - exp2
        data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
        
        return data

class RiskManager:
    """Manages risk and position sizing"""
    
    @staticmethod
    def calculate_position_size(account_size: float,
                              risk_per_trade: float,
                              entry_price: float,
                              stop_loss: float) -> float:
        """
        Calculate position size based on risk parameters.
        
        Args:
            account_size: Total account size
            risk_per_trade: Risk per trade as a percentage
            entry_price: Entry price
            stop_loss: Stop loss price
            
        Returns:
            Position size in units
        """
        risk_amount = account_size * risk_per_trade
        risk_per_unit = abs(entry_price - stop_loss)
        return risk_amount / risk_per_unit
    
    @staticmethod
    def calculate_stop_loss(entry_price: float,
                          atr: float,
                          multiplier: float = 2.0,
                          direction: str = 'long') -> float:
        """
        Calculate stop loss based on ATR.
        
        Args:
            entry_price: Entry price
            atr: Average True Range
            multiplier: ATR multiplier
            direction: Trade direction ('long' or 'short')
            
        Returns:
            Stop loss price
        """
        if direction == 'long':
            return entry_price - (atr * multiplier)
        else:
            return entry_price + (atr * multiplier)
    
    @staticmethod
    def calculate_trailing_stop(current_price: float,
                              atr: float,
                              multiplier: float = 2.0,
                              direction: str = 'long') -> float:
        """
        Calculate trailing stop based on ATR.
        
        Args:
            current_price: Current price
            atr: Average True Range
            multiplier: ATR multiplier
            direction: Trade direction ('long' or 'short')
            
        Returns:
            Trailing stop price
        """
        if direction == 'long':
            return current_price - (atr * multiplier)
        else:
            return current_price + (atr * multiplier) 