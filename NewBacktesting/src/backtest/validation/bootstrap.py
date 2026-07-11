"""
Bootstrap methods for significance testing and uncertainty quantification.
"""
import sys
from pathlib import Path

# Allow running this file directly as a script (python bootstrap.py)
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


class BootstrapValidator:
    """
    Bootstrap validation for strategy significance testing.
    """
    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Type[Strategy],
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0,
        n_bootstrap: int = 1000,
        block_size: int = 10
    ):
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.n_bootstrap = n_bootstrap
        self.block_size = block_size
        
    def _block_bootstrap(self, returns: pd.Series) -> pd.Series:
        """
        Generate block-bootstrap sample of returns.
        
        Args:
            returns: Original returns series
            
        Returns:
            Bootstrap sample returns
        """
        n = len(returns)
        n_blocks = n // self.block_size
        if n_blocks == 0:
            return returns
            
        blocks = [returns.iloc[i * self.block_size:(i + 1) * self.block_size] 
                  for i in range(n_blocks)]
        
        # If there's a partial block at the end
        if n % self.block_size != 0:
            blocks.append(returns.iloc[n_blocks * self.block_size:])
            
        # Sample blocks with replacement
        sampled_indices = np.random.choice(len(blocks), size=len(blocks), replace=True)
        bootstrap_sample = pd.concat([blocks[i] for i in sampled_indices], axis=0)
        
        # Ensure we have the same length as original
        return bootstrap_sample.iloc[:n]
        
    def run(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run bootstrap validation.
        
        Args:
            params: Strategy parameters to use
            
        Returns:
            Dictionary with bootstrap results
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
        
        # Generate bootstrap samples
        bootstrap_results = []
        bootstrap_sharpes = []
        bootstrap_returns = []
        
        # Get price returns to bootstrap
        price_returns = self.data["close"].pct_change().dropna()
        
        for i in range(self.n_bootstrap):
            # Bootstrap price returns
            boot_returns = self._block_bootstrap(price_returns)
            
            # Create synthetic price series
            boot_prices = (1 + boot_returns).cumprod()
            # Scale to match original price range
            boot_prices = boot_prices * (self.data["close"].iloc[-1] / boot_prices.iloc[-1])
            
            # Create synthetic OHLCV data
            boot_data = pd.DataFrame({
                "open": boot_prices * (1 + np.random.normal(0, 0.001, len(boot_prices))),
                "high": boot_prices * (1 + np.random.uniform(0, 0.01, len(boot_prices))),
                "low": boot_prices * (1 - np.random.uniform(0, 0.01, len(boot_prices))),
                "close": boot_prices,
                "volume": self.data["volume"].sample(frac=1, replace=True).values
            }, index=boot_returns.index)
            
            # Run backtest on synthetic data
            boot_backtest = Backtest(
                data=boot_data,
                strategy=self.strategy,
                initial_capital=self.initial_capital,
                commission=self.commission,
                slippage=self.slippage
            )
            boot_result = boot_backtest.run(params=params)
            
            if "error" not in boot_result:
                boot_metrics = boot_result["metrics"]
                bootstrap_results.append(boot_metrics)
                bootstrap_sharpes.append(boot_metrics.get("sharpe_ratio", 0))
                bootstrap_returns.append(boot_metrics.get("total_return", 0))
                
        # Calculate significance
        sharpe_pvalue = np.mean(np.array(bootstrap_sharpes) >= orig_sharpe)
        return_pvalue = np.mean(np.array(bootstrap_returns) >= orig_total_return)
        
        return {
            "original_metrics": orig_metrics,
            "n_bootstrap": self.n_bootstrap,
            "block_size": self.block_size,
            "n_valid_bootstraps": len(bootstrap_results),
            "bootstrap_sharpe_mean": np.mean(bootstrap_sharpes) if bootstrap_sharpes else 0,
            "bootstrap_sharpe_std": np.std(bootstrap_sharpes) if bootstrap_sharpes else 0,
            "bootstrap_return_mean": np.mean(bootstrap_returns) if bootstrap_returns else 0,
            "bootstrap_return_std": np.std(bootstrap_returns) if bootstrap_returns else 0,
            "sharpe_pvalue": sharpe_pvalue,
            "return_pvalue": return_pvalue
        }
