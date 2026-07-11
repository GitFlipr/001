"""
Test script for NewBacktesting system
"""
import sys
from pathlib import Path

# Add src and strategies to path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))
strategies_path = Path(__file__).parent.parent
sys.path.insert(0, str(strategies_path))

import pandas as pd
import numpy as np
from datetime import datetime
from backtest import (
    Backtest, 
    DataLoader, 
    DataQualityChecker,
    MarketRegimeDetector,
    Optimizer,
    WalkForwardValidator,
    RollingWindowValidator,
    BootstrapValidator,
    CombinatorialPurgedCV,
    PermutationTester,
    EpochValidator,
    DeflatedSharpeRatio,
    StrategyDiscovery
)
from strategies.trend_following import SMACrossover, EMACrossover
from strategies.mean_reversion import RSIMeanReversion
from strategies.breakout import BollingerBreakout


def generate_sample_data():
    """
    Generate sample OHLCV data for testing
    
    Returns:
        DataFrame with OHLCV data
    """
    # Generate dates
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 12, 31)
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    
    # Generate prices with random walk
    np.random.seed(42)
    base_price = 100.0
    returns = np.random.normal(0.001, 0.02, len(dates))
    close_prices = base_price * (1 + returns).cumprod()
    
    # Generate OHLC
    open_prices = close_prices * (1 + np.random.normal(0, 0.005, len(dates)))
    high_prices = np.maximum(open_prices, close_prices) * (1 + np.random.uniform(0, 0.01, len(dates)))
    low_prices = np.minimum(open_prices, close_prices) * (1 - np.random.uniform(0, 0.01, len(dates)))
    volume = np.random.randint(10000, 100000, len(dates))
    
    # Create DataFrame
    df = pd.DataFrame({
        "date": dates,
        "open": open_prices,
        "high": high_prices,
        "low": low_prices,
        "close": close_prices,
        "volume": volume
    })
    df = df.set_index("date")
    
    return df


def main():
    print("Testing NewBacktesting system...")
    print("=" * 70)
    
    # Generate sample data
    print("\n1. Generating sample data...")
    data = generate_sample_data()
    print(f"   Generated {len(data)} data points")
    
    # Test data quality checks
    print("\n2. Testing Data Quality Checks...")
    quality_checker = DataQualityChecker(data)
    quality_results = quality_checker.check_all()
    print(f"   Schema check: {quality_results['schema']['status']}")
    print(f"   Missing values: {quality_results['missing_values']['status']}")
    print(f"   Price consistency: {quality_results['price_consistency']['status']}")
    print(f"   Negative prices: {quality_results['negative_prices']['status']}")
    print(f"   Duplicates: {quality_results['duplicates']['status']}")
    print(f"   Index sorted: {quality_results['index_sorted']['status']}")
    
    # Test market regime detection
    print("\n3. Testing Market Regime Detection...")
    regime_detector = MarketRegimeDetector(data, n_regimes=3, window_size=50)
    regime_results = regime_detector.detect()
    if "error" not in regime_results:
        print(f"   Regimes detected: {regime_results['n_regimes']}")
        for reg, stats in regime_results['regime_stats'].items():
            print(f"   {reg}: {stats['percentage']:.1f}% of data")
    
    # Create and run backtest
    print("\n4. Creating and running backtest...")
    backtest = Backtest(
        data=data,
        strategy=SMACrossover,
        initial_capital=10000.0,
        commission=0.001,
        slippage=0.001
    )
    results = backtest.run(params={"short_window": 10, "long_window": 50})
    
    # Print results
    print("\n5. Backtest Results:")
    print("   " + "-" * 70)
    metrics = results["metrics"]
    print(f"   Total Return: {metrics['total_return_pct']:.2f}%")
    print(f"   Annual Return: {metrics['annual_return_pct']:.2f}%")
    print(f"   Volatility: {metrics['volatility_pct']:.2f}%")
    print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"   Sortino Ratio: {metrics['sortino_ratio']:.2f}")
    print(f"   Calmar Ratio: {metrics['calmar_ratio']:.2f}")
    print(f"   Sterling Ratio: {metrics['sterling_ratio']:.2f}")
    print(f"   Burke Ratio: {metrics['burke_ratio']:.2f}")
    print(f"   Omega Ratio: {metrics['omega_ratio']:.2f}")
    print(f"   Ulcer Index: {metrics['ulcer_index']:.2f}")
    print(f"   Pain Index: {metrics['pain_index']:.4f}")
    print(f"   Kelly Criterion: {metrics['kelly_criterion']:.2f}")
    print(f"   Max Drawdown: {metrics['max_drawdown_pct']:.2f}%")
    print(f"   Avg Drawdown: {metrics['avg_drawdown_pct']:.2f}%")
    print(f"   Win Rate: {metrics['win_rate']*100:.2f}%")
    print(f"   Profit Factor: {metrics['profit_factor']:.2f}")
    print(f"   Payoff Ratio: {metrics['payoff_ratio']:.2f}")
    print(f"   Expectancy: {metrics['expectancy']*100:.4f}%")
    print(f"   Number of Trades: {metrics['num_trades']}")
    print(f"   Avg Trade: {metrics['avg_trade_pct']:.4f}%")
    print(f"   Best Trade: {metrics['best_trade_pct']:.2f}%")
    print(f"   Worst Trade: {metrics['worst_trade_pct']:.2f}%")
    print(f"   Quality Score: {metrics['quality_score']:.1f}/10")
    if metrics.get('var_historical_99') is not None:
        print(f"   VaR (Historical 99%): {metrics['var_historical_99']:.4f}")
    if metrics.get('cvar_expected_shortfall_99') is not None:
        print(f"   CVaR (Expected Shortfall 99%): {metrics['cvar_expected_shortfall_99']:.4f}")
    
    # Test deflated Sharpe ratio
    print("\n6. Testing Deflated Sharpe Ratio...")
    dsr = DeflatedSharpeRatio(
        returns=results["returns"],
        n_trials=100
    )
    dsr_results = dsr.calculate()
    print(f"   Sharpe Ratio: {dsr_results['sharpe_ratio']:.2f}")
    print(f"   Deflated Sharpe Ratio: {dsr_results['deflated_sharpe_ratio']:.2f}")
    print(f"   P-value: {dsr_results['p_value']:.4f}")
    
    # Test combinatorial purged CV
    print("\n7. Testing Combinatorial Purged CV (CPCV)...")
    cpcv = CombinatorialPurgedCV(
        n_splits=10,
        purge_window=10,
        embargo_window=5
    )
    splits = cpcv.split(data)
    print(f"   Generated {len(splits)} splits")
    paths = cpcv.generate_combinatorial_paths(data)
    print(f"   Generated {len(paths)} combinatorial paths")
    
    # Test optimization
    print("\n8. Testing optimization...")
    optimizer = Optimizer(
        data=data,
        strategy=SMACrossover,
        initial_capital=10000.0,
        commission=0.001,
        slippage=0.001
    )
    param_grid = {
        "short_window": [5, 10, 15],
        "long_window": [30, 50, 70]
    }
    best_params, best_value, results_df = optimizer.grid_search(
        param_grid=param_grid,
        metric="sharpe_ratio"
    )
    print(f"   Best parameters: {best_params}")
    print(f"   Best Sharpe Ratio: {best_value:.2f}")
    
    # Test walk-forward validation
    print("\n9. Testing Walk-Forward Validation...")
    wf_validator = WalkForwardValidator(
        data=data,
        strategy=SMACrossover,
        initial_capital=10000.0,
        commission=0.001,
        slippage=0.001,
        train_window_min=180,
        test_window=30,
        step_size=30
    )
    wf_results = wf_validator.run(params=best_params)
    if "error" not in wf_results:
        print(f"   Walk-Forward Iterations: {wf_results['n_iterations']}")
        print(f"   Aggregate Sharpe: {wf_results['aggregate_metrics']['sharpe_ratio']:.2f}")
    
    # Test rolling window validation
    print("\n10. Testing Rolling Window Validation...")
    rw_validator = RollingWindowValidator(
        data=data,
        strategy=SMACrossover,
        initial_capital=10000.0,
        commission=0.001,
        slippage=0.001,
        train_window=180,
        test_window=30,
        step_size=30
    )
    rw_results = rw_validator.run(params=best_params)
    if "error" not in rw_results:
        print(f"   Rolling Window Iterations: {rw_results['n_iterations']}")
        print(f"   Aggregate Sharpe: {rw_results['aggregate_metrics']['sharpe_ratio']:.2f}")
    
    # Test bootstrap validation (reduced iterations for speed)
    print("\n11. Testing Bootstrap Validation...")
    boot_validator = BootstrapValidator(
        data=data,
        strategy=SMACrossover,
        initial_capital=10000.0,
        commission=0.001,
        slippage=0.001,
        n_bootstrap=100,
        block_size=10
    )
    boot_results = boot_validator.run(params=best_params)
    if "error" not in boot_results:
        print(f"   Original Sharpe: {boot_results['original_metrics']['sharpe_ratio']:.2f}")
        print(f"   Bootstrap Sharpe Mean: {boot_results['bootstrap_sharpe_mean']:.2f}")
        print(f"   Sharpe p-value: {boot_results['sharpe_pvalue']:.4f}")
    
    # Test permutation test (reduced iterations for speed)
    print("\n12. Testing Permutation Test...")
    perm_tester = PermutationTester(
        data=data,
        strategy=SMACrossover,
        initial_capital=10000.0,
        commission=0.001,
        slippage=0.001,
        n_permutations=50
    )
    perm_results = perm_tester.run(params=best_params)
    if "error" not in perm_results:
        print(f"   Original Sharpe: {perm_results['original_metrics']['sharpe_ratio']:.2f}")
        print(f"   Permutation Sharpe Mean: {perm_results['permutation_sharpe_mean']:.2f}")
        print(f"   Sharpe p-value: {perm_results['sharpe_pvalue']:.4f}")
        print(f"   Significant: {perm_results['significant']}")
    
    # Test epoch validation (reduced epochs for speed)
    print("\n13. Testing Epoch Validation...")
    epoch_validator = EpochValidator(
        data=data,
        strategy=SMACrossover,
        initial_capital=10000.0,
        commission=0.001,
        slippage=0.001,
        epochs=20,
        resampling_method="block_shuffle",
        block_size=50
    )
    epoch_results = epoch_validator.run(params=best_params)
    if "error" not in epoch_results:
        print(f"   Original Sharpe: {epoch_results['original_metrics']['sharpe_ratio']:.2f}")
        print(f"   Epoch Sharpe Mean: {epoch_results['sharpe_ratio']['mean']:.2f}")
        print(f"   Success Rate: {epoch_results['robustness']['success_rate']*100:.1f}%")
    
    print("\n" + "=" * 70)
    print("Test complete! NewBacktesting system is ready!")


if __name__ == "__main__":
    main()
