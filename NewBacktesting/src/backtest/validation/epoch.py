"""
Epoch-based analysis for strategy robustness testing.
"""
import sys
from pathlib import Path

# Allow running this file directly as a script (python epoch.py)
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


class EpochValidator:
    """
    Epoch-based validation for strategy robustness testing.
    """
    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Type[Strategy],
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0,
        epochs: int = 50,
        resampling_method: str = "block_shuffle",
        block_size: int = 50
    ):
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.epochs = epochs
        self.resampling_method = resampling_method
        self.block_size = block_size
        
    def _block_shuffle(self):
        """Block shuffle resampling to preserve temporal structure"""
        data = self.data.copy()
        n = len(data)
        if n < self.block_size:
            return data
            
        # Create blocks
        blocks = []
        for i in range(0, n, self.block_size):
            block = data.iloc[i:i + self.block_size]
            if len(block) >= self.block_size // 2:
                blocks.append(block)
                
        if not blocks:
            return data
            
        # Shuffle blocks
        np.random.shuffle(blocks)
        
        # Concatenate blocks
        resampled = pd.concat(blocks, ignore_index=False)
        resampled = resampled.sort_index()
        
        return resampled
        
    def _random_shuffle(self):
        """Random shuffle resampling"""
        return self.data.sample(frac=1).sort_index()
        
    def _resample(self):
        """Resample data using specified method"""
        if self.resampling_method == "block_shuffle":
            return self._block_shuffle()
        elif self.resampling_method == "random_shuffle":
            return self._random_shuffle()
        else:
            return self.data.copy()
            
    def _calculate_robustness_metrics(self, epoch_results):
        """Calculate robustness metrics"""
        returns = [r.get('total_return', 0) for r in epoch_results]
        sharpes = [r.get('sharpe_ratio', 0) for r in epoch_results]
        drawdowns = [r.get('max_drawdown', 0) for r in epoch_results]
        
        if not returns or len(returns) < 2:
            return {}
            
        # Coefficient of variation
        return_cv = np.std(returns) / max(abs(np.mean(returns)), 1e-10)
        sharpe_cv = np.std(sharpes) / max(abs(np.mean(sharpes)), 1e-10)
        
        # Success rate
        success_rate = np.mean([r > 0 for r in returns])
        
        return {
            'return_cv': return_cv,
            'sharpe_cv': sharpe_cv,
            'success_rate': success_rate
        }
        
    def _calculate_stability_metrics(self, epoch_results):
        """Calculate stability metrics"""
        returns = [r.get('total_return', 0) for r in epoch_results]
        
        if not returns or len(returns) < 3:
            return {}
            
        # Trend
        x = np.arange(len(returns))
        slope, _ = np.polyfit(x, returns, 1)
        
        return {
            'return_trend': slope,
            'return_volatility': np.std(returns)
        }
        
    def run(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run epoch validation.
        
        Args:
            params: Strategy parameters to use
            
        Returns:
            Dictionary with epoch results
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
        
        # Run epochs
        epoch_results = []
        epoch_metrics_list = []
        
        for i in range(self.epochs):
            # Resample data
            resampled = self._resample()
            
            # Run backtest
            epoch_backtest = Backtest(
                data=resampled,
                strategy=self.strategy,
                initial_capital=self.initial_capital,
                commission=self.commission,
                slippage=self.slippage
            )
            epoch_result = epoch_backtest.run(params=params)
            
            if "error" not in epoch_result:
                epoch_metrics = epoch_result["metrics"]
                epoch_results.append({
                    "epoch": i,
                    "total_return": epoch_metrics.get("total_return", 0),
                    "sharpe_ratio": epoch_metrics.get("sharpe_ratio", 0),
                    "max_drawdown": epoch_metrics.get("max_drawdown", 0)
                })
                epoch_metrics_list.append(epoch_metrics)
                
        # Calculate statistics
        returns = [r["total_return"] for r in epoch_results]
        sharpes = [r["sharpe_ratio"] for r in epoch_results]
        drawdowns = [r["max_drawdown"] for r in epoch_results]
        
        robustness_metrics = self._calculate_robustness_metrics(epoch_metrics_list)
        stability_metrics = self._calculate_stability_metrics(epoch_metrics_list)
        
        return {
            "original_metrics": orig_metrics,
            "epochs": self.epochs,
            "n_valid_epochs": len(epoch_results),
            "resampling_method": self.resampling_method,
            "return": {
                "mean": np.mean(returns) if returns else 0,
                "std": np.std(returns) if returns else 0,
                "min": np.min(returns) if returns else 0,
                "max": np.max(returns) if returns else 0,
                "median": np.median(returns) if returns else 0
            },
            "sharpe_ratio": {
                "mean": np.mean(sharpes) if sharpes else 0,
                "std": np.std(sharpes) if sharpes else 0,
                "min": np.min(sharpes) if sharpes else 0,
                "max": np.max(sharpes) if sharpes else 0,
                "median": np.median(sharpes) if sharpes else 0
            },
            "robustness": robustness_metrics,
            "stability": stability_metrics,
            "epoch_results": epoch_results
        }
