"""
NewBacktesting - A modern, modular, high-performance backtesting framework
"""
__version__ = "0.1.0"

from .core.backtest import Backtest
from .data.loader import DataLoader
from .data.quality import DataQualityChecker
from .data.regimes import MarketRegimeDetector
from .metrics.metrics import Metrics
from .metrics.deflated_sharpe import DeflatedSharpeRatio
from .strategies.base import Strategy
from .strategies.discovery import StrategyDiscovery
from .utils.visualization import Visualizer
from .utils.optimization import Optimizer
from .utils.indicators import (
    sma, ema, rsi, crossover, bollinger_bands, macd, atr, roc, stoch_rsi
)
from .validation.walk_forward import WalkForwardValidator
from .validation.rolling_window import RollingWindowValidator
from .validation.bootstrap import BootstrapValidator
from .validation.combinatorial_purged_cv import CombinatorialPurgedCV
from .validation.permutation import PermutationTester
from .validation.epoch import EpochValidator
from .validation.monte_carlo import MonteCarloSimulator
from .config import (
    PROJECT_ROOT,
    get_default_data_dir,
    get_default_results_dir,
    get_default_strategies_dir,
    ensure_directories,
)
from .batch_runner import BatchBacktestRunner

__all__ = [
    "Backtest",
    "DataLoader",
    "DataQualityChecker",
    "MarketRegimeDetector",
    "Metrics",
    "DeflatedSharpeRatio",
    "Strategy",
    "StrategyDiscovery",
    "Visualizer",
    "Optimizer",
    "sma", "ema", "rsi", "crossover", "bollinger_bands", "macd", "atr", "roc", "stoch_rsi",
    "WalkForwardValidator",
    "RollingWindowValidator",
    "BootstrapValidator",
    "CombinatorialPurgedCV",
    "PermutationTester",
    "EpochValidator",
    "MonteCarloSimulator",
    "PROJECT_ROOT",
    "get_default_data_dir",
    "get_default_results_dir",
    "get_default_strategies_dir",
    "ensure_directories",
    "BatchBacktestRunner",
]
