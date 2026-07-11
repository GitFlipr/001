"""
Permutation tests for strategy significance testing.
"""
import sys
from pathlib import Path

# Allow running this file directly as a script (python permutation.py)
if __name__ == "__main__" or __package__ is None or __package__ == "":
    _src_root = Path(__file__).resolve().parents[2]
    if str(_src_root) not in sys.path:
        sys.path.insert(0, str(_src_root))
    from backtest.core.backtest import Backtest
    from backtest.strategies.base import Strategy
else:
    from ..core.backtest import Backtest
    from ..strategies.base import Strategy

from typing import Dict, Any, List, Optional, Type
import pandas as pd
import numpy as np


class PermutationTester:
    """
    Permutation test for strategy significance testing.
    """
    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Type[Strategy],
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0,
        n_permutations: int = 100
    ):
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.n_permutations = n_permutations
        
    def run(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run permutation test.
        
        Args:
            params: Strategy parameters to use
            
        Returns:
            Dictionary with permutation results
        """
        params = params or {}
        
        # First run backtest on original data
        backtest = Backtest(
            data=self.data,
            strategy=self.strategy,
            initial_capital=self.initial_capital,
            commission=self.commission,
            slippage=self.slippage
        )
        orig_result = backtest.run(params=params)
        
        if "error" in orig_result:
            return orig_result
            
        orig_metrics = orig_result["metrics"]
        orig_sharpe = orig_metrics.get("sharpe_ratio", 0)
        orig_total_return = orig_metrics.get("total_return", 0)
        
        # Generate permutations
        permutation_results = []
        permutation_sharpes = []
        permutation_returns = []
        
        for i in range(self.n_permutations):
            # Shuffle price columns
            perm_data = self.data.copy()
            perm_data['close'] = perm_data['close'].sample(frac=1).values
            perm_data['open'] = perm_data['open'].sample(frac=1).values
            perm_data['high'] = perm_data['high'].sample(frac=1).values
            perm_data['low'] = perm_data['low'].sample(frac=1).values
            
            # Run backtest on permuted data
            perm_backtest = Backtest(
                data=perm_data,
                strategy=self.strategy,
                initial_capital=self.initial_capital,
                commission=self.commission,
                slippage=self.slippage
            )
            perm_result = perm_backtest.run(params=params)
            
            if "error" not in perm_result:
                perm_metrics = perm_result["metrics"]
                permutation_results.append(perm_metrics)
                permutation_sharpes.append(perm_metrics.get("sharpe_ratio", 0))
                permutation_returns.append(perm_metrics.get("total_return", 0))
                
        # Calculate p-values
        sharpe_pvalue = np.mean(np.array(permutation_sharpes) >= orig_sharpe) if permutation_sharpes else 1.0
        return_pvalue = np.mean(np.array(permutation_returns) >= orig_total_return) if permutation_returns else 1.0
        
        # Overall significance
        significant = sharpe_pvalue < 0.05 and return_pvalue < 0.05
        
        return {
            "original_metrics": orig_metrics,
            "n_permutations": self.n_permutations,
            "n_valid_permutations": len(permutation_results),
            "permutation_sharpe_mean": np.mean(permutation_sharpes) if permutation_sharpes else 0,
            "permutation_sharpe_std": np.std(permutation_sharpes) if permutation_sharpes else 0,
            "permutation_return_mean": np.mean(permutation_returns) if permutation_returns else 0,
            "permutation_return_std": np.std(permutation_returns) if permutation_returns else 0,
            "sharpe_pvalue": sharpe_pvalue,
            "return_pvalue": return_pvalue,
            "significant": significant
        }
