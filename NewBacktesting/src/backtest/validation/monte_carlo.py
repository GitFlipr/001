"""
Monte Carlo simulation for strategy risk and uncertainty quantification.

Simulates many random equity-curve paths from either:
  - block-bootstrap resampling of observed returns (no distribution assumption), or
  - a fitted parametric distribution (normal / t-distribution).

Follows the Phase 5 blueprint: answers "how much variance and tail risk do we
get under this strategy or distribution across many paths?"
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow running this file directly as a script (python monte_carlo.py)
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

from typing import Dict, Any, List, Optional, Tuple, Type
import numpy as np
import pandas as pd

try:
    from scipy import stats as _scipy_stats
    _SCIPY_AVAILABLE = True
except ImportError:
    _SCIPY_AVAILABLE = False


class MonteCarloSimulator:
    """
    Monte Carlo simulation for strategy outcome distributions.

    Two simulation modes
    -------------------
    ``"block_bootstrap"``  (default, non-parametric)
        Resample blocks of the observed strategy returns with replacement to
        preserve autocorrelation structure, then build synthetic equity curves.

    ``"parametric"``
        Fit a normal or Student-t distribution to the observed returns and draw
        i.i.d. samples.  Requires scipy for the t-distribution; falls back to
        normal if scipy is unavailable.

    Parameters
    ----------
    data : pd.DataFrame
        OHLCV data used to run the baseline backtest.
    strategy : Type[Strategy]
        Strategy class to evaluate.
    initial_capital : float
        Starting equity, default 10 000.
    commission : float
        Round-trip commission rate, default 0.001 (0.1 %).
    slippage : float
        Slippage rate, default 0.0.
    n_simulations : int
        Number of Monte Carlo paths, default 1 000.
    block_size : int
        Block length for block-bootstrap resampling, default 20 bars.
    simulation_mode : str
        ``"block_bootstrap"`` or ``"parametric"``.
    dist : str
        Distribution for parametric mode: ``"normal"`` or ``"t"``.
    seed : int or None
        Random seed for reproducibility.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Type[Strategy],
        initial_capital: float = 10_000.0,
        commission: float = 0.001,
        slippage: float = 0.0,
        n_simulations: int = 1_000,
        block_size: int = 20,
        simulation_mode: str = "block_bootstrap",
        dist: str = "normal",
        seed: Optional[int] = None,
    ) -> None:
        self.data = data
        self.strategy = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.n_simulations = n_simulations
        self.block_size = block_size
        self.simulation_mode = simulation_mode
        self.dist = dist
        self.seed = seed

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _run_baseline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run a single backtest on the original data and return results."""
        bt = Backtest(
            data=self.data,
            strategy=self.strategy,
            initial_capital=self.initial_capital,
            commission=self.commission,
            slippage=self.slippage,
        )
        return bt.run(params=params)

    def _block_bootstrap_returns(
        self, returns: np.ndarray, rng: np.random.Generator
    ) -> np.ndarray:
        """
        Draw one block-bootstrap sample of the same length as *returns*.

        Blocks are chosen with replacement; a partial last block is kept if
        the total length is not a multiple of block_size.
        """
        n = len(returns)
        block_size = min(self.block_size, n)
        n_blocks = int(np.ceil(n / block_size))

        # Starting indices of all available blocks
        max_start = max(1, n - block_size + 1)
        starts = rng.integers(0, max_start, size=n_blocks)

        sampled = np.concatenate(
            [returns[s: s + block_size] for s in starts]
        )
        return sampled[:n]

    def _parametric_returns(
        self, returns: np.ndarray, rng: np.random.Generator
    ) -> np.ndarray:
        """Draw i.i.d. samples from a fitted parametric distribution."""
        n = len(returns)
        if self.dist == "t" and _SCIPY_AVAILABLE:
            df, loc, scale = _scipy_stats.t.fit(returns)
            return _scipy_stats.t.rvs(df, loc=loc, scale=scale, size=n,
                                      random_state=rng.integers(2**31))
        # Normal fallback
        mu, sigma = returns.mean(), returns.std(ddof=1)
        sigma = sigma if sigma > 0 else 1e-10
        return rng.normal(loc=mu, scale=sigma, size=n)

    def _equity_curve_from_returns(self, sim_returns: np.ndarray) -> np.ndarray:
        """Convert an array of period returns to an equity curve."""
        return self.initial_capital * np.cumprod(1.0 + sim_returns)

    @staticmethod
    def _max_drawdown(equity: np.ndarray) -> float:
        peak = np.maximum.accumulate(equity)
        dd = (equity - peak) / peak
        return float(dd.min())

    @staticmethod
    def _sharpe(returns: np.ndarray, ann_factor: float = 365.25) -> float:
        mu = returns.mean()
        sigma = returns.std(ddof=1)
        if sigma == 0:
            return 0.0
        return float((mu * ann_factor) / (sigma * np.sqrt(ann_factor)))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run the Monte Carlo simulation.

        Parameters
        ----------
        params : dict, optional
            Strategy parameters forwarded to the backtest engine.

        Returns
        -------
        dict with keys:

        ``original_metrics``
            Metrics from a single backtest on the unmodified data.
        ``n_simulations``
            Number of completed paths.
        ``simulation_mode``
            Mode used (``"block_bootstrap"`` or ``"parametric"``).
        ``final_equity``
            Distribution stats for final equity across all paths.
        ``total_return``
            Distribution stats for total return (fraction) across all paths.
        ``max_drawdown``
            Distribution stats for maximum drawdown across all paths.
        ``sharpe_ratio``
            Distribution stats for annualised Sharpe across all paths.
        ``var_95`` / ``var_99``
            Value-at-Risk on final equity at the 5 % and 1 % quantiles.
        ``cvar_95`` / ``cvar_99``
            Conditional VaR (Expected Shortfall) at the same quantiles.
        ``prob_profit``
            Fraction of paths that end with a positive total return.
        ``prob_drawdown_gt_20pct``
            Fraction of paths that experience a drawdown worse than -20 %.
        ``equity_paths``
            (n_simulations × T) float array of full equity curves.
        ``percentile_paths``
            Dict of named percentile equity curves (5, 25, 50, 75, 95).
        """
        params = params or {}
        rng = np.random.default_rng(self.seed)

        # ---- baseline run ------------------------------------------------
        baseline = self._run_baseline(params)
        if "error" in baseline:
            return baseline

        orig_metrics = baseline["metrics"]
        strategy_returns: pd.Series = baseline["returns"]
        obs_returns = strategy_returns.values.astype(float)
        n = len(obs_returns)

        # ---- simulate paths ----------------------------------------------
        all_final_equity: List[float] = []
        all_total_return: List[float] = []
        all_max_dd: List[float] = []
        all_sharpe: List[float] = []
        equity_paths: List[np.ndarray] = []

        for _ in range(self.n_simulations):
            if self.simulation_mode == "parametric":
                sim_ret = self._parametric_returns(obs_returns, rng)
            else:
                sim_ret = self._block_bootstrap_returns(obs_returns, rng)

            eq = self._equity_curve_from_returns(sim_ret)
            equity_paths.append(eq)

            final_eq = float(eq[-1])
            all_final_equity.append(final_eq)
            all_total_return.append((final_eq - self.initial_capital) / self.initial_capital)
            all_max_dd.append(self._max_drawdown(eq))
            all_sharpe.append(self._sharpe(sim_ret))

        # ---- aggregate statistics ----------------------------------------
        def _stats(arr: List[float]) -> Dict[str, float]:
            a = np.array(arr)
            return {
                "mean":   float(a.mean()),
                "std":    float(a.std(ddof=1)),
                "min":    float(a.min()),
                "p5":     float(np.percentile(a, 5)),
                "p25":    float(np.percentile(a, 25)),
                "median": float(np.median(a)),
                "p75":    float(np.percentile(a, 75)),
                "p95":    float(np.percentile(a, 95)),
                "max":    float(a.max()),
            }

        fe_arr = np.array(all_final_equity)
        var_95 = float(np.percentile(fe_arr, 5))
        var_99 = float(np.percentile(fe_arr, 1))
        cvar_95 = float(fe_arr[fe_arr <= var_95].mean()) if (fe_arr <= var_95).any() else var_95
        cvar_99 = float(fe_arr[fe_arr <= var_99].mean()) if (fe_arr <= var_99).any() else var_99

        prob_profit = float(np.mean(np.array(all_total_return) > 0))
        prob_dd_gt20 = float(np.mean(np.array(all_max_dd) < -0.20))

        # ---- percentile equity paths -------------------------------------
        paths_matrix = np.array(equity_paths)          # (n_sim, T)
        pct_paths = {
            "p5":     paths_matrix[np.argsort(fe_arr)[int(0.05 * self.n_simulations)]].tolist(),
            "p25":    paths_matrix[np.argsort(fe_arr)[int(0.25 * self.n_simulations)]].tolist(),
            "median": paths_matrix[np.argsort(fe_arr)[int(0.50 * self.n_simulations)]].tolist(),
            "p75":    paths_matrix[np.argsort(fe_arr)[int(0.75 * self.n_simulations)]].tolist(),
            "p95":    paths_matrix[np.argsort(fe_arr)[int(0.95 * self.n_simulations)]].tolist(),
        }

        return {
            "original_metrics":       orig_metrics,
            "n_simulations":          self.n_simulations,
            "simulation_mode":        self.simulation_mode,
            "block_size":             self.block_size if self.simulation_mode == "block_bootstrap" else None,
            "dist":                   self.dist if self.simulation_mode == "parametric" else None,
            "final_equity":           _stats(all_final_equity),
            "total_return":           _stats(all_total_return),
            "max_drawdown":           _stats(all_max_dd),
            "sharpe_ratio":           _stats(all_sharpe),
            "var_95":                 var_95,
            "var_99":                 var_99,
            "cvar_95":                cvar_95,
            "cvar_99":                cvar_99,
            "prob_profit":            prob_profit,
            "prob_drawdown_gt_20pct": prob_dd_gt20,
            "equity_paths":           paths_matrix,
            "percentile_paths":       pct_paths,
        }

    def summary(self, results: Optional[Dict[str, Any]] = None,
                params: Optional[Dict[str, Any]] = None) -> str:
        """
        Return a formatted text summary.  Runs the simulation if *results*
        is not supplied.
        """
        if results is None:
            results = self.run(params or {})
        if "error" in results:
            return f"Monte Carlo failed: {results['error']}"

        orig = results["original_metrics"]
        tr   = results["total_return"]
        mdd  = results["max_drawdown"]
        sr   = results["sharpe_ratio"]

        lines = [
            "=" * 60,
            "Monte Carlo Simulation Summary",
            "=" * 60,
            f"Mode            : {results['simulation_mode']}",
            f"Paths simulated : {results['n_simulations']:,}",
            f"",
            f"--- Original backtest ---",
            f"  Total return  : {orig.get('total_return_pct', 0):.2f} %",
            f"  Sharpe ratio  : {orig.get('sharpe_ratio', 0):.3f}",
            f"  Max drawdown  : {orig.get('max_drawdown_pct', 0):.2f} %",
            f"",
            f"--- Simulated total return ---",
            f"  Mean          : {tr['mean']*100:.2f} %",
            f"  Std dev       : {tr['std']*100:.2f} %",
            f"  5th pct       : {tr['p5']*100:.2f} %",
            f"  Median        : {tr['median']*100:.2f} %",
            f"  95th pct      : {tr['p95']*100:.2f} %",
            f"",
            f"--- Simulated max drawdown ---",
            f"  Mean          : {mdd['mean']*100:.2f} %",
            f"  Worst 5 %     : {mdd['p5']*100:.2f} %",
            f"",
            f"--- Simulated Sharpe ratio ---",
            f"  Mean          : {sr['mean']:.3f}",
            f"  5th pct       : {sr['p5']:.3f}",
            f"  95th pct      : {sr['p95']:.3f}",
            f"",
            f"--- Risk metrics (final equity) ---",
            f"  VaR  95 %     : {results['var_95']:,.2f}",
            f"  VaR  99 %     : {results['var_99']:,.2f}",
            f"  CVaR 95 %     : {results['cvar_95']:,.2f}",
            f"  CVaR 99 %     : {results['cvar_99']:,.2f}",
            f"",
            f"--- Probabilities ---",
            f"  P(profit)     : {results['prob_profit']*100:.1f} %",
            f"  P(DD > 20%)   : {results['prob_drawdown_gt_20pct']*100:.1f} %",
            "=" * 60,
        ]
        return "\n".join(lines)
