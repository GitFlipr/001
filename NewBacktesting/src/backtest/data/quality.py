"""
Data quality checks.
"""
from typing import Dict, Any, List
import pandas as pd
import numpy as np


class DataQualityChecker:
    """
    Data quality checks for OHLCV data.
    """
    def __init__(self, data: pd.DataFrame):
        """
        Initialize data quality checker.
        
        Args:
            data: OHLCV DataFrame
        """
        self.data = data
    
    def check_all(self) -> Dict[str, Any]:
        """
        Run all data quality checks.
        
        Returns:
            Dictionary with check results
        """
        results = {}
        
        results["schema"] = self.check_schema()
        results["missing_values"] = self.check_missing_values()
        results["price_consistency"] = self.check_price_consistency()
        results["negative_prices"] = self.check_negative_prices()
        results["duplicates"] = self.check_duplicates()
        results["index_sorted"] = self.check_index_sorted()
        results["summary"] = self.get_summary()
        
        return results
    
    def check_schema(self) -> Dict[str, Any]:
        """
        Check schema of data.
        
        Returns:
            Schema check results
        """
        required_columns = ["open", "high", "low", "close", "volume"]
        missing = [col for col in required_columns if col not in self.data.columns]
        present = [col for col in required_columns if col in self.data.columns]
        
        return {
            "status": "pass" if len(missing) == 0 else "fail",
            "required_columns": required_columns,
            "missing_columns": missing,
            "present_columns": present,
            "extra_columns": [col for col in self.data.columns if col not in required_columns]
        }
    
    def check_missing_values(self) -> Dict[str, Any]:
        """
        Check for missing values.
        
        Returns:
            Missing values check results
        """
        missing = self.data.isnull().sum()
        total_missing = missing.sum()
        total_cells = self.data.size
        
        return {
            "status": "pass" if total_missing == 0 else "warn",
            "total_missing": total_missing,
            "missing_percentage": (total_missing / total_cells * 100) if total_cells > 0 else 0,
            "missing_by_column": missing.to_dict()
        }
    
    def check_price_consistency(self) -> Dict[str, Any]:
        """
        Check price consistency (high >= low, high >= open, etc.)
        
        Returns:
            Price consistency check results
        """
        if "high" not in self.data.columns or "low" not in self.data.columns:
            return {"status": "skip", "reason": "Missing high/low columns"}
        
        invalid_high_low = (self.data["high"] < self.data["low"]).sum()
        
        invalid_high = 0
        if "open" in self.data.columns:
            invalid_high += (self.data["high"] < self.data["open"]).sum()
        if "close" in self.data.columns:
            invalid_high += (self.data["high"] < self.data["close"]).sum()
        
        invalid_low = 0
        if "open" in self.data.columns:
            invalid_low += (self.data["low"] > self.data["open"]).sum()
        if "close" in self.data.columns:
            invalid_low += (self.data["low"] > self.data["close"]).sum()
        
        total_invalid = invalid_high_low + invalid_high + invalid_low
        
        return {
            "status": "pass" if total_invalid == 0 else "warn",
            "invalid_high_low": invalid_high_low,
            "invalid_high_vs_open_close": invalid_high,
            "invalid_low_vs_open_close": invalid_low,
            "total_invalid": total_invalid
        }
    
    def check_negative_prices(self) -> Dict[str, Any]:
        """
        Check for negative prices/volume.
        
        Returns:
            Negative values check results
        """
        negative_counts = {}
        for col in ["open", "high", "low", "close", "volume"]:
            if col in self.data.columns:
                negative_counts[col] = (self.data[col] < 0).sum()
        
        total_negative = sum(negative_counts.values())
        
        return {
            "status": "pass" if total_negative == 0 else "fail",
            "negative_by_column": negative_counts,
            "total_negative": total_negative
        }
    
    def check_duplicates(self) -> Dict[str, Any]:
        """
        Check for duplicates in index and data.
        
        Returns:
            Duplicates check results
        """
        duplicate_index = self.data.index.duplicated().sum()
        duplicate_rows = self.data.duplicated().sum()
        
        return {
            "status": "pass" if duplicate_index == 0 and duplicate_rows == 0 else "warn",
            "duplicate_index_entries": duplicate_index,
            "duplicate_rows": duplicate_rows
        }
    
    def check_index_sorted(self) -> Dict[str, Any]:
        """
        Check if index is sorted.
        
        Returns:
            Index sorted check results
        """
        is_sorted = self.data.index.equals(self.data.index.sort_values())
        
        return {
            "status": "pass" if is_sorted else "fail",
            "is_sorted": is_sorted
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get data summary.
        
        Returns:
            Summary dictionary
        """
        summary = {
            "n_rows": len(self.data),
            "start_date": self.data.index.min() if len(self.data) > 0 else None,
            "end_date": self.data.index.max() if len(self.data) > 0 else None
        }
        
        for col in ["open", "high", "low", "close", "volume"]:
            if col in self.data.columns:
                summary[f"{col}_min"] = self.data[col].min()
                summary[f"{col}_max"] = self.data[col].max()
                summary[f"{col}_mean"] = self.data[col].mean()
        
        return summary
