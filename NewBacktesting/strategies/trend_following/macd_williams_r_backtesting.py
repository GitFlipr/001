import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from macd_williams_strategy import trading_strategy, backtest_strategy

def advanced_performance_analysis(data):
    """
    Perform comprehensive performance analysis of the trading strategy
    
    Parameters:
    - data: DataFrame with trading strategy results
    
    Returns:
    - Dictionary with detailed performance metrics
    """
    # Filter trades
    trades = data[data['Exit_Price'].notna()]
    
    # Advanced Performance Metrics
    performance_metrics = {
        'Total Trades': len(trades),
        'Winning Trades': len(trades[trades['Profit_Loss'] > 0]),
        'Losing Trades': len(trades[trades['Profit_Loss'] <= 0]),
        'Win Rate (%)': len(trades[trades['Profit_Loss'] > 0]) / len(trades) * 100 if len(trades) > 0 else 0,
        'Average Profit (%)': trades['Profit_Loss'].mean() if len(trades) > 0 else 0,
        'Median Profit (%)': trades['Profit_Loss'].median() if len(trades) > 0 else 0,
        'Total Profit/Loss (%)': trades['Profit_Loss'].sum(),
        'Largest Winning Trade (%)': trades['Profit_Loss'].max() if len(trades) > 0 else 0,
        'Largest Losing Trade (%)': trades['Profit_Loss'].min() if len(trades) > 0 else 0,
        'Standard Deviation of Profits (%)': trades['Profit_Loss'].std() if len(trades) > 0 else 0,
        'Sharpe Ratio': trades['Profit_Loss'].mean() / trades['Profit_Loss'].std() if trades['Profit_Loss'].std() != 0 else 0
    }
    
    return performance_metrics

def plot_performance_analysis(data):
    """
    Create comprehensive visualizations of strategy performance
    
    Parameters:
    - data: DataFrame with trading strategy results
    """
    # Filter trades
    trades = data[data['Exit_Price'].notna()]
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    plt.subplots_adjust(hspace=0.4, wspace=0.3)
    
    # 1. Profit Distribution Histogram
    sns.histplot(trades['Profit_Loss'], kde=True, ax=axes[0, 0])
    axes[0, 0].set_title('Trade Profit Distribution')
    axes[0, 0].set_xlabel('Trade Profit (%)')
    axes[0, 0].set_ylabel('Frequency')
    
    # 2. Cumulative Profit Tracking
    trades['Cumulative_Profit'] = trades['Profit_Loss'].cumsum()
    trades['Cumulative_Profit'].plot(ax=axes[0, 1])
    axes[0, 1].set_title('Cumulative Profit Over Trades')
    axes[0, 1].set_xlabel('Trade Number')
    axes[0, 1].set_ylabel('Cumulative Profit (%)')
    
    # 3. Trade Duration and Profit Scatter
    trades['Trade_Duration'] = range(len(trades))
    sns.scatterplot(data=trades, x='Trade_Duration', y='Profit_Loss', ax=axes[1, 0])
    axes[1, 0].set_title('Trade Duration vs Profit')
    axes[1, 0].set_xlabel('Trade Number')
    axes[1, 0].set_ylabel('Trade Profit (%)')
    
    # 4. Box Plot of Trade Profits
    sns.boxplot(x=trades['Profit_Loss'], ax=axes[1, 1])
    axes[1, 1].set_title('Trade Profit Distribution')
    axes[1, 1].set_xlabel('Trade Profit (%)')
    
    plt.suptitle('MACD Williams %R Strategy Performance Analysis', fontsize=16)
    plt.tight_layout()
    plt.show()

def parameter_sensitivity_analysis(sample_data, parameter_ranges):
    """
    Perform parameter sensitivity analysis
    
    Parameters:
    - sample_data: DataFrame with price data
    - parameter_ranges: Dictionary of parameter ranges to test
    
    Returns:
    - DataFrame with performance results for different parameter combinations
    """
    sensitivity_results = []
    
    # Iterate through parameter combinations
    for macd_short_window in parameter_ranges.get('macd_short_window', [12]):
        for macd_long_window in parameter_ranges.get('macd_long_window', [26]):
            for macd_signal_window in parameter_ranges.get('macd_signal_window', [9]):
                for williams_r_window in parameter_ranges.get('williams_r_window', [14]):
                    # Modify the trading strategy to accept parameters
                    def custom_trading_strategy(data):
                        from macd_williams_strategy import calculate_macd, calculate_williams_r
                        
                        # Calculate indicators with custom parameters
                        macd = calculate_macd(
                            data['Close'], 
                            short_window=macd_short_window, 
                            long_window=macd_long_window, 
                            signal_window=macd_signal_window
                        )
                        williams_r = calculate_williams_r(
                            data['High'], 
                            data['Low'], 
                            data['Close'], 
                            window=williams_r_window
                        )
                        
                        # Combine indicators
                        data = pd.concat([data, macd, williams_r], axis=1)
                        
                        # Initialize trading signal columns
                        data['Position'] = 0
                        data['Entry_Price'] = np.nan
                        data['Exit_Price'] = np.nan
                        data['Profit_Loss'] = np.nan
                        
                        # Trading logic with default thresholds
                        for i in range(1, len(data)):
                            # Buy signal
                            if (macd['MACD'].iloc[i] > macd['Signal'].iloc[i] and 
                                williams_r.iloc[i] < -80 and 
                                data['Position'].iloc[i-1] == 0):
                                data.loc[data.index[i], 'Position'] = 1
                                data.loc[data.index[i], 'Entry_Price'] = data['Close'].iloc[i]
                            
                            # Sell/Exit signal
                            if data['Position'].iloc[i-1] == 1:
                                # Exit conditions
                                exit_conditions = (
                                    (macd['MACD'].iloc[i] < macd['Signal'].iloc[i]) or
                                    (williams_r.iloc[i] > -20) or
                                    (data['Close'].iloc[i] >= data['Entry_Price'].iloc[i] * 1.02) or
                                    (data['Close'].iloc[i] <= data['Entry_Price'].iloc[i] * 0.99)
                                )
                                
                                if exit_conditions:
                                    data.loc[data.index[i], 'Position'] = 0
                                    data.loc[data.index[i], 'Exit_Price'] = data['Close'].iloc[i]
                                    
                                    # Calculate profit/loss percentage
                                    profit_loss_pct = ((data['Exit_Price'].iloc[i] - data['Entry_Price'].iloc[i]) / 
                                                       data['Entry_Price'].iloc[i]) * 100
                                    data.loc[data.index[i], 'Profit_Loss'] = profit_loss_pct
                        
                        return data
                    
                    # Run strategy with custom parameters
                    strategy_results = custom_trading_strategy(sample_data.copy())
                    performance = backtest_strategy(strategy_results)
                    
                    # Store results
                    sensitivity_results.append({
                        'MACD Short Window': macd_short_window,
                        'MACD Long Window': macd_long_window,
                        'MACD Signal Window': macd_signal_window,
                        'Williams %R Window': williams_r_window,
                        'Total Trades': performance['Total Trades'],
                        'Winning Trades': performance['Winning Trades'],
                        'Win Rate (%)': performance['Win Rate'],
                        'Average Profit (%)': performance['Average Profit']
                    })
    
    return pd.DataFrame(sensitivity_results)

def main():
    # Simulate sample data (replace with your actual financial data)
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    np.random.seed(42)
    
    sample_data = pd.DataFrame({
        'Date': dates,
        'Close': np.cumsum(np.random.normal(0, 1, len(dates))) + 100,
        'High': np.cumsum(np.random.normal(0, 1, len(dates))) + 102,
        'Low': np.cumsum(np.random.normal(0, 1, len(dates))) + 98
    })
    sample_data.set_index('Date', inplace=True)
    
    # Run strategy
    strategy_results = trading_strategy(sample_data)
    
    # Advanced Performance Analysis
    print("\nDetailed Performance Analysis:")
    performance_metrics = advanced_performance_analysis(strategy_results)
    for metric, value in performance_metrics.items():
        print(f"{metric}: {value}")
    
    # Performance Visualization
    plot_performance_analysis(strategy_results)
    
    # Parameter Sensitivity Analysis
    print("\nRunning Parameter Sensitivity Analysis...")
    parameter_ranges = {
        'macd_short_window': [10, 12, 15],
        'macd_long_window': [24, 26, 30],
        'macd_signal_window': [7, 9, 11],
        'williams_r_window': [12, 14, 16]
    }
    sensitivity_results = parameter_sensitivity_analysis(sample_data, parameter_ranges)
    
    # Save sensitivity analysis results
    sensitivity_results.to_csv('parameter_sensitivity_results.csv', index=False)
    print("\nParameter Sensitivity Analysis Complete. Results saved to 'parameter_sensitivity_results.csv'")
