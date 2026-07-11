import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from keltner_cmf_scalper import KeltnerCMFStrategy, generate_sample_data

def performance_analysis(results):
    """
    Perform detailed performance analysis of the trading strategy
    
    :param results: Backtest results dictionary
    :return: Dictionary with performance metrics
    """
    trades_df = results['Trades']
    
    # Advanced Performance Metrics
    performance_metrics = {
        'Total Trades': len(trades_df),
        'Total Return (%)': results['Total Return (%)'],
        'Average Trade Profit (%)': trades_df['Profit'].mean(),
        'Median Trade Profit (%)': trades_df['Profit'].median(),
        'Win Rate (%)': (trades_df['Profit'] > 0).mean() * 100,
        'Largest Winning Trade (%)': trades_df['Profit'].max(),
        'Largest Losing Trade (%)': trades_df['Profit'].min(),
        'Standard Deviation of Trades (%)': trades_df['Profit'].std(),
        'Sharpe Ratio': trades_df['Profit'].mean() / trades_df['Profit'].std() if trades_df['Profit'].std() != 0 else 0
    }
    
    return performance_metrics

def plot_performance(results):
    """
    Create visualizations of strategy performance
    
    :param results: Backtest results dictionary
    """
    trades_df = results['Trades']
    
    # Subplot configuration
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    plt.subplots_adjust(hspace=0.3, wspace=0.3)
    
    # 1. Trade Profit Distribution
    sns.histplot(trades_df['Profit'], kde=True, ax=axes[0, 0])
    axes[0, 0].set_title('Trade Profit Distribution')
    axes[0, 0].set_xlabel('Trade Profit (%)')
    axes[0, 0].set_ylabel('Frequency')
    
    # 2. Cumulative Profit Tracking
    trades_df['Cumulative_Profit'] = trades_df['Profit'].cumsum()
    trades_df['Cumulative_Profit'].plot(ax=axes[0, 1])
    axes[0, 1].set_title('Cumulative Profit Over Trades')
    axes[0, 1].set_xlabel('Trade Number')
    axes[0, 1].set_ylabel('Cumulative Profit (%)')
    
    # 3. Channel Width vs Profit Scatter
    sns.scatterplot(data=trades_df, x='Channel Width', y='Profit', ax=axes[1, 0])
    axes[1, 0].set_title('Channel Width vs Trade Profit')
    axes[1, 0].set_xlabel('Keltner Channel Width')
    axes[1, 0].set_ylabel('Trade Profit (%)')
    
    # 4. Box Plot of Trade Profits
    sns.boxplot(x=trades_df['Profit'], ax=axes[1, 1])
    axes[1, 1].set_title('Trade Profit Box Plot')
    axes[1, 1].set_xlabel('Trade Profit (%)')
    
    plt.suptitle('Keltner CMF Strategy Performance Analysis', fontsize=16)
    plt.tight_layout()
    plt.show()

def parameter_sensitivity_analysis(data, param_ranges):
    """
    Perform parameter sensitivity analysis
    
    :param data: Market data DataFrame
    :param param_ranges: Dictionary of parameter ranges to test
    :return: DataFrame with performance results
    """
    sensitivity_results = []
    
    for keltner_window in param_ranges.get('keltner_window', [20]):
        for keltner_atr_multiplier in param_ranges.get('keltner_atr_multiplier', [2]):
            for cmf_window in param_ranges.get('cmf_window', [20]):
                for cmf_threshold in param_ranges.get('cmf_threshold', [0]):
                    # Initialize and run strategy
                    strategy = KeltnerCMFStrategy(
                        data, 
                        keltner_window=keltner_window, 
                        keltner_atr_multiplier=keltner_atr_multiplier, 
                        cmf_window=cmf_window
                    )
                    strategy.generate_signals(cmf_threshold=cmf_threshold)
                    results = strategy.backtest()
                    
                    # Store results
                    sensitivity_results.append({
                        'Keltner Window': keltner_window,
                        'ATR Multiplier': keltner_atr_multiplier,
                        'CMF Window': cmf_window,
                        'CMF Threshold': cmf_threshold,
                        'Total Return (%)': results['Total Return (%)'],
                        'Number of Trades': results['Number of Trades'],
                        'Average Trade Profit (%)': results['Average Trade Profit (%)']
                    })
    
    return pd.DataFrame(sensitivity_results)

def main():
    # Generate sample data
    data = generate_sample_data()
    
    # Initialize strategy with default parameters
    strategy = KeltnerCMFStrategy(data)
    
    # Generate trading signals
    strategy.generate_signals()
    
    # Backtest
    results = strategy.backtest()
    
    # Performance Analysis
    print("\nDetailed Performance Metrics:")
    performance_metrics = performance_analysis(results)
    for metric, value in performance_metrics.items():
        print(f"{metric}: {value:.2f}")
    
    # Plot Performance
    plot_performance(results)
    
    # Parameter Sensitivity Analysis
    print("\nRunning Parameter Sensitivity Analysis...")
    param_ranges = {
        'keltner_window': [10, 20, 30],
        'keltner_atr_multiplier': [1.5, 2, 2.5],
        'cmf_window': [15, 20, 25],
        'cmf_threshold': [-0.1, 0, 0.1]
    }
    sensitivity_results = parameter_sensitivity_analysis(data, param_ranges)
    
    # Save sensitivity analysis results
    sensitivity_results.to_csv('parameter_sensitivity_results.csv', index=False)
    print("\nParameter Sensitivity Analysis Complete. Results saved to 'parameter_sensitivity_results.csv'")
