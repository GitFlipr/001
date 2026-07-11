"""
Strategy optimization utilities
"""
from typing import Dict, Any, List, Tuple, Optional, Type, Callable
import pandas as pd
from itertools import product
from ..core.backtest import Backtest
from ..strategies.base import Strategy


class Optimizer:
    """
    Strategy parameter optimization
    """
    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Type[Strategy],
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0
    ):
        """
        Initialize optimizer
        
        Args:
            data: OHLCV data
            strategy: Strategy class
            initial_capital: Starting capital
            commission: Commission rate
            slippage: Slippage rate
        """
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage

    def grid_search(
        self,
        param_grid: Dict[str, List[Any]],
        metric: str = "sharpe_ratio",
        maximize: bool = True
    ) -> Tuple[Dict[str, Any], float, pd.DataFrame]:
        """
        Grid search optimization
        
        Args:
            param_grid: Dictionary of parameter ranges
            metric: Metric to optimize
            maximize: Whether to maximize (True) or minimize (False) the metric
            
        Returns:
            (best_params, best_value, results_df)
        """
        # Generate all parameter combinations
        param_names = list(param_grid.keys())
        param_values = [param_grid[name] for name in param_names]
        combinations = list(product(*param_values))
        
        results = []
        
        # Run backtest for each combination
        for combo in combinations:
            params = dict(zip(param_names, combo))
            backtest = Backtest(
                data=self.data,
                strategy=self.strategy,
                initial_capital=self.initial_capital,
                commission=self.commission,
                slippage=self.slippage
            )
            backtest_results = backtest.run(params)
            metrics = backtest_results["metrics"]
            metric_value = metrics.get(metric, 0.0)
            
            results.append({
                **params,
                **{k: v for k, v in metrics.items() if k in [
                    "sharpe_ratio", "total_return_pct", "max_drawdown_pct",
                    "annual_return_pct", "win_rate", "profit_factor"
                ]}
            })
        
        # Create DataFrame
        results_df = pd.DataFrame(results)
        
        # Find best parameters
        if maximize:
            best_idx = results_df[metric].idxmax()
        else:
            best_idx = results_df[metric].idxmin()
        
        best_params = dict(zip(param_names, combinations[best_idx]))
        best_value = results_df.iloc[best_idx][metric]
        
        return best_params, best_value, results_df
