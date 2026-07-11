import pandas as pd
import numpy as np
from bollinger_roc_scalper import BollingerRocStrategy, generate_sample_data

def load_historical_data(file_path):
    """
    Load historical stock data from a CSV file
    
    :param file_path: Path to the CSV file
    :return: DataFrame with price data
    """
    try:
        data = pd.read_csv(file_path)
        data['Date'] = pd.to_datetime(data['Date'])
        data.set_index('Date', inplace=True)
        if 'Close' not in data.columns:
            raise ValueError("CSV data does not contain 'Close' prices.")
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def run_comprehensive_backtest(data, start_date, end_date, 
                                initial_capital=100, 
                                parameter_grid=None):
    """
    Run comprehensive backtest with parameter optimization
    
    :param data: DataFrame with historical price data
    :param start_date: Start date for backtesting
    :param end_date: End date for backtesting
    :param initial_capital: Starting capital for simulation
    :param parameter_grid: Dictionary of parameters to test
    :return: DataFrame of backtest results
    """
    # Ensure the data is filtered by the specified date range
    data = data.loc[start_date:end_date]
    
    if data is None or data.empty:
        print("No data available for the specified date range.")
        return None
    
    # Default parameter grid if not provided
    if parameter_grid is None:
        parameter_grid = {
            'bb_window': [15, 20, 25],
            'bb_std_dev': [1.5, 2, 2.5],
            'roc_window': [10, 14, 18],
            'bb_touch_sensitivity': [0.005, 0.01, 0.02],
            'take_profit_pct': [0.02, 0.03, 0.04],
            'stop_loss_method': ['fixed', 'atr'],
            'stop_loss_pct': [0.01, 0.015, 0.02]
        }
    
    # Collect backtest results
    results = []
    
    # Iterate through parameter combinations
    for bb_window in parameter_grid['bb_window']:
        for std_dev in parameter_grid['bb_std_dev']:
            for roc_window in parameter_grid['roc_window']:
                for touch_sens in parameter_grid['bb_touch_sensitivity']:
                    for tp_pct in parameter_grid['take_profit_pct']:
                        for sl_method in parameter_grid['stop_loss_method']:
                            for sl_pct in parameter_grid['stop_loss_pct']:
                                # Create strategy instance
                                strategy = BollingerRocStrategy(
                                    data, 
                                    bb_window=bb_window, 
                                    bb_std_dev=std_dev, 
                                    roc_window=roc_window
                                )
                                
                                # Generate signals
                                strategy.generate_signals(
                                    bb_touch_sensitivity=touch_sens
                                )
                                
                                # Backtest
                                backtest_result = strategy.backtest(
                                    initial_capital=initial_capital,
                                    take_profit_pct=tp_pct,
                                    stop_loss_method=sl_method,
                                    stop_loss_pct=sl_pct
                                )
                                
                                # Prepare result record
                                result_record = {
                                    'BB_Window': bb_window,
                                    'BB_Std_Dev': std_dev,
                                    'ROC_Window': roc_window,
                                    'BB_Touch_Sensitivity': touch_sens,
                                    'Take_Profit_Pct': tp_pct,
                                    'Stop_Loss_Method': sl_method,
                                    'Stop_Loss_Pct': sl_pct,
                                    'Initial_Capital': backtest_result['Initial Capital'],
                                    'Final_Capital': backtest_result['Final Capital'],
                                    'Total_Return_Pct': backtest_result['Total Return (%)'],
                                    'Num_Trades': backtest_result['Number of Trades'],
                                    'Avg_Trade_Profit_Pct': backtest_result['Average Trade Profit (%)']
                                }
                                
                                results.append(result_record)
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Sort results by total return
    results_df = results_df.sort_values('Total_Return_Pct', ascending=False)
    
    return results_df

def analyze_results(results_df, top_n=5):
    """
    Analyze and print top performing parameter combinations
    
    :param results_df: DataFrame of backtest results
    :param top_n: Number of top results to display
    """
    if results_df is None or results_df.empty:
        print("No results to analyze.")
        return
    
    print("\n--- Top {} Parameter Combinations ---".format(top_n))
    print(results_df.head(top_n))
    
    # Descriptive statistics
    print("\n--- Descriptive Statistics ---")
    print(results_df[['Total_Return_Pct', 'Num_Trades', 'Avg_Trade_Profit_Pct']].describe())

def main():
    # Example usage
    file_path = "C:\\Users\\andre\\CryptoBots\\eth_data.csv"  # Path to CSV file
    start_date = "2022-01-01"
    end_date = "2023-12-31"
    
    # Load historical data from CSV
    data = load_historical_data(file_path)
    
    # Run comprehensive backtest
    results_df = run_comprehensive_backtest(data, start_date, end_date)
    
    # Analyze results
    analyze_results(results_df)
