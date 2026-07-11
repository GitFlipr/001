from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
import numpy as np
import talib
import logging
from datetime import datetime
import re

class ADXTrendStrategy(Strategy):
    """
    ADX Trend Strategy with Moving Average Filters
    
    Entry Rules:
    1. Long: Fast MA > Slow MA, ADX > threshold, DI+ > DI-
    2. Short: Fast MA < Slow MA, ADX > threshold, DI- > DI+
    
    Exit Rules:
    1. Long: ADX falls below threshold or DI+ < DI-
    2. Short: ADX falls below threshold or DI- < DI+
    """
    
    # Strategy parameters
    fast_ma = 50  # Fast moving average period
    slow_ma = 200  # Slow moving average period
    adx_period = 14  # ADX period
    adx_threshold = 25  # ADX threshold for trend strength
    atr_period = 14  # ATR period for stop loss
    atr_multiplier = 2.0  # ATR multiplier for stop loss
    
    def init(self):
        # Initialize logging
        self.logger = logging.getLogger(__name__)
        
        try:
            # Calculate moving averages
            self.fast_ma = self.I(talib.SMA, self.data.Close, timeperiod=self.fast_ma)
            self.slow_ma = self.I(talib.SMA, self.data.Close, timeperiod=self.slow_ma)
            
            # Calculate ADX and DI+/- for trend direction
            self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_period)
            self.plus_di = self.I(talib.PLUS_DI, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_period)
            self.minus_di = self.I(talib.MINUS_DI, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_period)
            
            # Calculate ATR for stop loss
            self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
            
            self.logger.info("Strategy initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error in init(): {str(e)}")
            raise
    def next(self):
        if len(self.data) < 80:
            return
        try:
            price = self.data.Close[-1]
            
            # Entry conditions
            if not self.position:
                # Long entry conditions
                if (self.fast_ma[-1] > self.slow_ma[-1] and
                    self.adx[-1] > self.adx_threshold and
                    self.plus_di[-1] > self.minus_di[-1]):
                    
                    # Calculate position size based on ATR
                    atr_value = self.atr[-1]
                    stop_loss = price - (atr_value * self.atr_multiplier)
                    take_profit = price + (atr_value * (self.atr_multiplier * 1.5))
                    
                    # Ensure proper order of SL, price, and TP
                    if stop_loss < price < take_profit:
                        self.buy(sl=stop_loss, tp=take_profit)
                        self.logger.info(f"Long entry at {price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
                
                # Short entry conditions
                elif (self.fast_ma[-1] < self.slow_ma[-1] and
                      self.adx[-1] > self.adx_threshold and
                      self.minus_di[-1] > self.plus_di[-1]):
                    
                    # Calculate position size based on ATR
                    atr_value = self.atr[-1]
                    stop_loss = price + (atr_value * self.atr_multiplier)
                    take_profit = price - (atr_value * (self.atr_multiplier * 1.5))
                    
                    # Ensure proper order of TP, price, and SL
                    if take_profit < price < stop_loss:
                        self.sell(sl=stop_loss, tp=take_profit)
                        self.logger.info(f"Short entry at {price:.2f}, SL: {stop_loss:.2f}, TP: {take_profit:.2f}")
            
            # Exit conditions
            else:
                if self.position.is_long:
                    # Exit if trend weakens
                    if (self.adx[-1] < self.adx_threshold or
                        self.plus_di[-1] < self.minus_di[-1]):
                        self.position.close()
                        self.logger.info(f"Long exit at {price:.2f}")
                
                elif self.position.is_short:
                    # Exit if trend weakens
                    if (self.adx[-1] < self.adx_threshold or
                        self.minus_di[-1] < self.plus_di[-1]):
                        self.position.close()
                        self.logger.info(f"Short exit at {price:.2f}")
                        
        except Exception as e:
            self.logger.error(f"Error in next(): {str(e)}")
            raise

def load_data(filepath):
    """
    Load and preprocess data for the strategy.
    
    Args:
        filepath (str): Path to CSV file or directory containing CSV files
        
    Returns:
        dict: Dictionary of DataFrames keyed by (asset, timeframe)
    """
    import os
    import pandas as pd
    import re
    
    # Check if path is a directory
    if os.path.isdir(filepath):
        print(f"Loading CSV files from directory: {filepath}")
        
        # Get all CSV files in the directory
        files = [f for f in os.listdir(filepath) if f.endswith('.csv')]
        
        if not files:
            raise FileNotFoundError(f"No CSV files found in directory: {filepath}")
            
        print(f"Found {len(files)} files: {', '.join(files)}")
        
        data_dict = {}
        # Load each CSV file
        for file in files:
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
                
                file_path = os.path.join(filepath, file)
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
                
                data_dict[key] = df
                print(f"  Added {len(df)} rows from {file}")
                
            except Exception as e:
                print(f"  Error loading {file}: {str(e)}")
        
        if not data_dict:
            raise ValueError("No valid data could be loaded from any CSV file")
            
        return data_dict
        
    else:
        # Load single file
        print(f"Loading single file: {filepath}")
        data = pd.read_csv(filepath, index_col='Date', parse_dates=True)
        
        # Convert numeric columns
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for column in numeric_columns:
            if column in data.columns:
                data[column] = pd.to_numeric(data[column], errors='coerce')
        
        # Drop rows with NaN values
        data = data.dropna()
        
        # Create a single entry dictionary
        return {('SINGLE', '1D'): data}

def run_backtest(data, cash=1000000, commission=0.002):
    """
    Run the backtest for the ADX Trend strategy.
    
    Args:
        data (pd.DataFrame): Preprocessed data
        cash (float): Initial cash (increased for high-priced assets)
        commission (float): Commission per trade
        
    Returns:
        dict: Backtest results
    """
    # Calculate position size based on average price
    avg_price = data['Close'].mean()
    position_size = cash / avg_price
    
    bt = Backtest(data, ADXTrendStrategy, cash=cash, commission=commission)
    results = bt.run()
    # bt.plot()  # Uncomment to show plot
    return results
