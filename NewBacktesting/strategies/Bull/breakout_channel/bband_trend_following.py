from backtesting import Backtest, Strategy
import pandas as pd
import numpy as np
import talib
import os
import json
import re

class BBTrendFollowingStrategy(Strategy):
    """
    Bollinger Band Trend Following Strategy
    
    Entry Rules:
    1. Long: Price near lower band in uptrend, with volume confirmation
    2. Short: Price near upper band in downtrend, with volume confirmation
    
    Exit Rules:
    1. Long: Price reaches middle band or trailing stop hit
    2. Short: Price reaches middle band or trailing stop hit
    """
    
    # Strategy parameters
    bb_period = 20
    bb_std = 2.0
    trend_period = 50  # Period for trend confirmation
    atr_period = 14
    atr_multiplier = 2.0
    volume_ma_period = 20
    
    def init(self):
        # Calculate Bollinger Bands
        self.bb_upper, self.bb_middle, self.bb_lower = self.I(talib.BBANDS, self.data.Close,
                                                         timeperiod=self.bb_period,
                                                         nbdevup=self.bb_std,
                                                         nbdevdn=self.bb_std)
        
        # Calculate trend using longer-term SMA
        self.trend_sma = self.I(talib.SMA, self.data.Close, timeperiod=self.trend_period)
        
        # Calculate ATR for stop loss
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # Calculate volume SMA for confirmation
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_ma_period)
    
    def next(self):
        price = self.data.Close[-1]
        volume = self.data.Volume[-1]
        
        # Check if we have a position
        if not self.position:
            # Long entry conditions
            if (price <= self.bb_lower[-1] and  # Price near lower band
                price > self.trend_sma[-1] and   # Uptrend
                volume > self.volume_sma[-1]):   # Volume confirmation
                
                # Calculate position size based on ATR
                atr_value = self.atr[-1]
                stop_loss = price - (atr_value * self.atr_multiplier)
                take_profit = self.bb_middle[-1]  # Target middle band
                
                # Ensure proper order of SL, price, and TP
                if stop_loss < price < take_profit:
                    self.buy(sl=stop_loss, tp=take_profit)
            
            # Short entry conditions
            elif (price >= self.bb_upper[-1] and  # Price near upper band
                  price < self.trend_sma[-1] and  # Downtrend
                  volume > self.volume_sma[-1]):  # Volume confirmation
                
                # Calculate position size based on ATR
                atr_value = self.atr[-1]
                stop_loss = price + (atr_value * self.atr_multiplier)
                take_profit = self.bb_middle[-1]  # Target middle band
                
                # Ensure proper order of TP, price, and SL
                if take_profit < price < stop_loss:
                    self.sell(sl=stop_loss, tp=take_profit)
        
        # Exit conditions
        else:
            if self.position.is_long:
                # Exit if trend reverses
                if price < self.trend_sma[-1]:
                    self.position.close()
            
            elif self.position.is_short:
                # Exit if trend reverses
                if price > self.trend_sma[-1]:
                    self.position.close()

def load_data(filepath):
    """
    Load and preprocess data for the strategy from all subfolders.
    
    Args:
        filepath (str): Path to directory containing CSV files in subfolders

        Returns:
        dict: Dictionary of DataFrames keyed by (asset, timeframe)
    """
    if not os.path.isdir(filepath):
        raise FileNotFoundError(f"Directory not found: {filepath}")
    
    data_dict = {}
    
    # Walk through all subdirectories
    for root, dirs, files in os.walk(filepath):
        # Get all CSV files in current directory
        csv_files = [f for f in files if f.endswith('.csv')]
        
        if not csv_files:
            continue
            
        print(f"Processing directory: {root}")
        print(f"Found {len(csv_files)} CSV files")
        
        # Load each CSV file
        for file in csv_files:
            try:
                # Extract asset and timeframe from filename
                match = re.match(r'([A-Z]+)_(\d+[mhd])_', file)
                if match:
                    asset, timeframe = match.groups()
                    # Convert '1d' to '1D' for consistency
                    if timeframe == '1d':
                        timeframe = '1D'
                    key = (asset, timeframe)
                else:
                    print(f"Warning: Could not parse asset and timeframe from filename: {file}")
                    continue
                
                file_path = os.path.join(root, file)
                print(f"Loading: {file}")
                
                # Load single file
                df = pd.read_csv(file_path, index_col='Date', parse_dates=True)
                
                # Convert numeric columns
                numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                for column in numeric_columns:
                    if column in df.columns:
                        df[column] = pd.to_numeric(df[column], errors='coerce')
                
                # Drop rows with NaN values
                df = df.dropna()
                
                # Add file info
                df['Source'] = file
                
                # If we already have data for this asset/timeframe, append it
                if key in data_dict:
                    data_dict[key] = pd.concat([data_dict[key], df])
                    print(f"  Appended {len(df)} rows to existing data for {asset} {timeframe}")
                else:
                    data_dict[key] = df
                    print(f"  Added {len(df)} rows from {file}")
                
            except Exception as e:
                print(f"  Error loading {file}: {str(e)}")
    
    if not data_dict:
        raise ValueError("No valid data could be loaded from any CSV file")
    
    # Sort each DataFrame by date
    for key in data_dict:
        data_dict[key] = data_dict[key].sort_index()
    
    # Print summary of loaded data
    print("\nData Summary:")
    for (asset, timeframe), df in data_dict.items():
        print(f"{asset} {timeframe}: {len(df)} rows from {df.index.min()} to {df.index.max()}")
    
    return data_dict

def save_results(results, asset, timeframe, params, output_dir):
    """Save backtest results in standard format."""
    # Create results directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Prepare results dictionary
    results_dict = {
        'Start': str(results['Start']),
        'End': str(results['End']),
        'Duration': str(results['Duration']),
        'Exposure Time [%]': float(results['Exposure Time [%]']),
        'Equity Final [$]': float(results['Equity Final [$]']),
        'Equity Peak [$]': float(results['Equity Peak [$]']),
        'Return [%]': float(results['Return [%]']),
        'Buy & Hold Return [%]': float(results['Buy & Hold Return [%]']),
        'Return (Ann.) [%]': float(results['Return (Ann.) [%]']),
        'Volatility (Ann.) [%]': float(results['Volatility (Ann.) [%]']),
        'Sharpe Ratio': float(results['Sharpe Ratio']),
        'Sortino Ratio': float(results['Sortino Ratio']),
        'Calmar Ratio': float(results['Calmar Ratio']),
        'Max. Drawdown [%]': float(results['Max. Drawdown [%]']),
        'Avg. Drawdown [%]': float(results['Avg. Drawdown [%]']),
        'Max. Drawdown Duration': str(results['Max. Drawdown Duration']),
        'Avg. Drawdown Duration': str(results['Avg. Drawdown Duration']),
        '# Trades': int(results['# Trades']),
        'Win Rate [%]': float(results['Win Rate [%]']),
        'Best Trade [%]': float(results['Best Trade [%]']),
        'Worst Trade [%]': float(results['Worst Trade [%]']),
        'Avg. Trade [%]': float(results['Avg. Trade [%]']),
        'Max. Trade Duration': str(results['Max. Trade Duration']),
        'Avg. Trade Duration': str(results['Avg. Trade Duration']),
        'Profit Factor': float(results['Profit Factor']),
        'Expectancy [%]': float(results['Expectancy [%]']),
        'SQN': float(results['SQN']),
        'Kelly Criterion': float(results['Kelly Criterion']),
        'Parameters': params
    }
    
    # Save to JSON file
    output_file = os.path.join(output_dir, f'{asset}_{timeframe}_bb_trend_following_results.json')
    with open(output_file, 'w') as f:
        json.dump(results_dict, f, indent=4)
    
    return output_file
