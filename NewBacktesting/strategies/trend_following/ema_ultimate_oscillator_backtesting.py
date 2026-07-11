import pandas as pd
import numpy as np
import yfinance as yf
from ema_ultimate_oscillator_scalper import (
    trading_strategy, 
    backtest_strategy
)

def load_historical_data(ticker, start_date, end_date):
    """
    Load historical stock data from Yahoo Finance
    
    :param ticker: Stock ticker symbol
    :param start_date: Start date for data retrieval
    :param end_date: End date for data retrieval
    :return: DataFrame with price data
    """
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        data.reset_index(inplace=True)
        data.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
        return data[['Date', 'Open', 'High', 'Low', 'Close']]
    except Exception as e:
        print(f"Error downloading data: {e}")
        return None

def run_comprehensive_backtest(ticker, start_date, end_date, 
                                initial_capital=10000, 
                                parameter_grid=None):
    """
    Run comprehensive backtest with parameter optimization
    
    :param ticker: Stock ticker symbol
    :param start_date: Start date for backtesting
    :param end_date: End date for backtesting
    :param initial_capital: Starting capital for simulation
    :param parameter_grid: Dictionary of parameters to test
    :return: DataFrame of backtest results
    """
    # Load historical data
    data = load_historical_data(ticker, start_date, end_date)
    
    if data is None:
        return None
    
    # Set data index
    data.set_index('Date', inplace=True)
    
    # Default parameter grid if not provided
    if parameter_grid is None:
        parameter_grid = {
            'ema_window': [10, 20, 30],
            'atr_window': [10, 14, 21],
            'atr_multiplier': [1.5, 2, 2.5]
        }
    
    # Collect backtest results
    results = []
    
    # Iterate through parameter combinations
    for ema_window in parameter_grid['ema_window']:
        for atr_window in parameter_grid['atr_window']:
            for atr_multiplier in parameter_grid['atr_multiplier']:
                try:
                    # Run trading strategy
                    strategy_results = trading_strategy(
                        data.copy(), 
                        ema_window=ema_window, 
                        atr_window=atr_window, 
                        atr_multiplier=atr_multiplier
                    )
                    
                    # Backtest strategy
                    performance = backtest_strategy(strategy_results)
                    
                    # Prepare result record
                    result_record = {
                        'EMA_Window': ema_window,
                        'ATR_Window': atr_window,
                        'ATR_Multiplier': atr_multiplier,
                        'Total_Trades': performance['Total Trades'],
                        'Winning_Trades': performance['Winning Trades'],
                        'Losing_Trades': performance['Losing Trades'],
                        'Win_Rate': performance['Win Rate'],
                        'Average_Profit': performance['Average Profit'],
                        'Total_Profit_Loss': performance['Total Profit/Loss'],
                        'Max_Drawdown': performance['Max Drawdown'],
                        'Max_Profit': performance['Max Profit']
                    }
                    
                    results.append(result_record)
                except Exception as e:
                    print(f"Error in backtesting with parameters {result_record}: {e}")
    
    # Convert results to DataFrame