"""
Strategy base class
"""
from abc import ABC, abstractmethod
from typing import Any, Dict
import pandas as pd


class Strategy(ABC):
    """
    Base class for all trading strategies
    """
    def __init__(self, params: Dict[str, Any] = None):
        """
        Initialize strategy with optional parameters
        
        Args:
            params: Dictionary of strategy parameters
        """
        self.params = params or {}
        self.data: pd.DataFrame = None

    def set_data(self, data: pd.DataFrame):
        """
        Set OHLCV data for the strategy
        
        Args:
            data: DataFrame with OHLCV data
        """
        self.data = data

    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """
        Generate trading signals
        
        Returns:
            DataFrame with 'signal' column (1 for long, -1 for short, 0 for no position)
        """
        pass
