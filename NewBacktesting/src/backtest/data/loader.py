"""
Data loading and preprocessing module
"""
from pathlib import Path
from typing import Optional, Union
import pandas as pd
import numpy as np

from backtest.config import get_default_data_dir


class DataLoader:
    @staticmethod
    def default_data_dir() -> Path:
        return get_default_data_dir()

    @staticmethod
    def from_directory(
        directory: Union[str, Path, None] = None,
        pattern: str = "*.csv",
        recursive: bool = True,
    ) -> list[pd.DataFrame]:
        base_dir = Path(directory or get_default_data_dir())
        files = sorted(base_dir.rglob(pattern) if recursive else base_dir.glob(pattern))
        frames = []
        for file_path in files:
            frames.append(DataLoader.from_csv(file_path))
        return frames

    """
    Load and preprocess OHLCV data
    """
    def __init__(self):
        pass

    @staticmethod
    def from_csv(
        path: Union[str, Path],
        date_column: str = "date",
        open_column: str = "open",
        high_column: str = "high",
        low_column: str = "low",
        close_column: str = "close",
        volume_column: str = "volume"
    ) -> pd.DataFrame:
        """
        Load OHLCV data from CSV file
        
        Args:
            path: Path to CSV file
            date_column: Name of date column
            open_column: Name of open column
            high_column: Name of high column
            low_column: Name of low column
            close_column: Name of close column
            volume_column: Name of volume column
            
        Returns:
            DataFrame with standardized column names and datetime index
        """
        df = pd.read_csv(path)
        
        # Standardize column names
        df = df.rename(columns={
            date_column: "date",
            open_column: "open",
            high_column: "high",
            low_column: "low",
            close_column: "close",
            volume_column: "volume"
        })
        
        # Convert date to datetime
        df["date"] = pd.to_datetime(df["date"], utc=True)
        
        # Set index and sort
        df = df.set_index("date").sort_index()
        
        # Ensure numerical types
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Drop rows with missing values
        df = df.dropna()
        
        return df

    @staticmethod
    def from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess existing DataFrame
        
        Args:
            df: Input DataFrame with OHLCV data
            
        Returns:
            Standardized DataFrame
        """
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Ensure we have required columns
        required_cols = ["open", "high", "low", "close", "volume"]
        for col in required_cols:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
        
        # Ensure datetime index
        if not isinstance(df.index, pd.DatetimeIndex):
            if "date" in df.columns:
                df["date"] = pd.to_datetime(df["date"], utc=True)
                df = df.set_index("date")
            else:
                raise ValueError("DataFrame must have datetime index or 'date' column")
        
        # Sort index
        df = df.sort_index()
        
        # Ensure numerical types
        for col in required_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Drop rows with missing values
        df = df.dropna()
        
        return df
