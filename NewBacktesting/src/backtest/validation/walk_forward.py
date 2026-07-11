"""
Walk-Forward (Rolling Origin) Validation.

Trains on expanding training window and tests on a fixed test horizon, rolling forward.
"""
import sys
from pathlib import Path

# Allow running this file directly as a script (python walk_forward.py)
if __name__ == "__main__" or __package__ is None or __package__ == "":
    _src_root = Path(__file__).resolve().parents[2]
    if str(_src_root) not in sys.path:
        sys.path.insert(0, str(_src_root))
    from backtest.core.backtest import Backtest
    from backtest.strategies.base import Strategy
    from backtest.metrics.metrics import Metrics
else:
    from ..core.backtest import Backtest
    from ..strategies.base import Strategy
    from ..metrics.metrics import Metrics

from typing import Dict, Any, List, Optional, Type
import pandas as pd
import numpy as np


class WalkForwardValidator:
    """
    Walk-forward validation using expanding training window and fixed test horizon.
    """
    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Type[Strategy],
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0,
        train_window_min: int = 90,
        test_window: int = 30,
        step_size: int = 30
    ):
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.train_window_min = train_window_min
        self.test_window = test_window
        self.step_size = step_size
        
    def run(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run walk-forward validation.
        
        Args:
            params: Strategy parameters to use
            
        Returns:
            Dictionary with validation results
        """
        params = params or {}
        n = len(self.data)
        results = []
        all_returns = []
        all_equity = []
        
        # Calculate split points
        start_idx = self.train_window_min
        splits = []
        while start_idx + self.test_window <= n:
            splits.append(start_idx)
            start_idx += self.step_size
            
        if not splits:
            return {"error": "Insufficient data for walk-forward validation"}
            
        # Run each walk-forward iteration
        for i, split_idx in enumerate(splits):
            # Split data
            train_data = self.data.iloc[:split_idx]
            test_data = self.data.iloc[split_idx:split_idx + self.test_window]
            
            # Run backtest on test data
            # Note: For true walk-forward, you would optimize params on train,
            # but here we use fixed params for simplicity
            backtest = Backtest(
                data=test_data,
                strategy=self.strategy,
                initial_capital=self.initial_capital,
                commission=self.commission,
                slippage=self.slippage
            )
            backtest_result = backtest.run(params=params)
            
            if "error" in backtest_result:
                continue
                
            results.append({
                "iteration": i,
                "train_start": train_data.index[0],
                "train_end": train_data.index[-1],
                "test_start": test_data.index[0],
                "test_end": test_data.index[-1],
                "metrics": backtest_result["metrics"]
            })
            
            all_returns.extend(backtest_result["returns"])
            
        # Calculate aggregate metrics
        if not results:
            return {"error": "No valid walk-forward iterations completed"}
            
        returns_series = pd.Series(all_returns, index=self.data.iloc[splits[0]:].index)
        agg_metrics = Metrics(returns_series).calculate_all()
        
        return {
            "n_iterations": len(results),
            "train_window_min": self.train_window_min,
            "test_window": self.test_window,
            "step_size": self.step_size,
            "iterations": results,
            "aggregate_metrics": agg_metrics
        }
