"""
Combinatorial purged cross-validation (CPCV).

Based on: Lopez de Prado — Advances in Financial Machine Learning.
"""
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np


class CombinatorialPurgedCV:
    """
    Combinatorial purged cross-validation.
    """
    def __init__(
        self,
        n_splits: int = 10,
        purge_window: int = 10,
        embargo_window: int = 0
    ):
        """
        Initialize CPCV.
        
        Args:
            n_splits: Number of splits (must be at least 6)
            purge_window: Purge window in bars to prevent leakage
            embargo_window: Embargo window in bars to prevent leakage
        """
        self.n_splits = n_splits
        self.purge_window = purge_window
        self.embargo_window = embargo_window
    
    def split(
        self,
        data: pd.DataFrame
    ) -> List[Tuple[np.ndarray, np.ndarray]]:
        """
        Generate splits.
        
        Args:
            data: DataFrame with datetime index
            
        Returns:
            List of (train_indices, test_indices) tuples
        """
        n = len(data)
        indices = np.arange(n)
        
        # Create splits
        splits = []
        split_size = n // self.n_splits
        
        for i in range(self.n_splits):
            test_start = i * split_size
            test_end = min((i + 1) * split_size, n)
            test_indices = indices[test_start:test_end]
            
            # Calculate train indices with purging and embargo
            train_indices = []
            
            # Before test
            before_start = 0
            before_end = max(0, test_start - self.purge_window)
            if before_end > before_start:
                train_indices.extend(indices[before_start:before_end])
            
            # After test with embargo
            after_start = min(n, test_end + self.purge_window + self.embargo_window)
            after_end = n
            if after_end > after_start:
                train_indices.extend(indices[after_start:after_end])
            
            splits.append((np.array(train_indices), test_indices))
        
        return splits
    
    def generate_combinatorial_paths(
        self,
        data: pd.DataFrame
    ) -> List[List[int]]:
        """
        Generate combinatorial paths for bagging.
        
        Args:
            data: DataFrame with datetime index
            
        Returns:
            List of paths where each path is a list of split indices
        """
        from itertools import combinations
        
        # Generate all combinations of (n_splits//2) splits
        k = self.n_splits // 2
        all_paths = list(combinations(range(self.n_splits), k))
        
        return all_paths
