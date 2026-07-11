import os
import json
import logging
import re
import datetime
import pandas as pd
import talib # Use talib for consistency with basic_backtest.py

from backtesting import Backtest, Strategy
from backtesting.lib import crossover

# Configure basic logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class BullBearEMARsiScalping(Strategy):
    """
    Bull/Bear Market Scalping Strategy using EMA and RSI.

    Entry Rules:
    - Bull: Short EMA > Long EMA and RSI crosses above buy level (oversold).
    - Bear: Short EMA < Long EMA and RSI crosses below sell level (overbought).

    Exit Rules:
    - Close long if short EMA crosses below long EMA or RSI is overbought.
    - Close short if short EMA crosses above long EMA or RSI is oversold.
    """
    # Define parameters for the strategy
    short_ema_period = 5  # Short-term EMA period
    long_ema_period = 20  # Longer-term EMA period
    rsi_period = 14       # RSI period
    rsi_buy_level = 40    # RSI level for buy signal
    rsi_sell_level = 60   # RSI level for sell signal
    # Add other parameters like stop_loss_pct, take_profit_pct if needed

    def init(self):
        self.logger = logging.getLogger(__name__)
        try:
            # Calculate EMAs and RSI using talib
            close = self.data.Close
            self.short_ema = self.I(talib.EMA, close, timeperiod=self.short_ema_period)
            self.long_ema = self.I(talib.EMA, close, timeperiod=self.long_ema_period)
            self.rsi = self.I(talib.RSI, close, timeperiod=self.rsi_period)
            self.logger.info("Strategy initialized successfully")
        except Exception as e:
            self.logger.error(f"Error in init(): {str(e)}")
            raise

    def next(self):
        try:
            price = self.data.Close[-1]

            # Entry conditions
            if not self.position:
                # Bull Market Strategy: Buy on pullbacks
                if self.short_ema[-1] > self.long_ema[-1] and crossover(self.rsi, self.rsi_buy_level):
                    self.buy()

                # Bear Market Strategy: Sell on rallies
                elif self.short_ema[-1] < self.long_ema[-1] and crossover(self.rsi_sell_level, self.rsi):
                    self.sell()

            # Exit conditions
            else:
                # Close long position if short EMA crosses below long EMA or RSI goes overbought
                if self.position.is_long and (crossover(self.long_ema, self.short_ema) or self.rsi[-1] > self.rsi_sell_level):
                     self.position.close()

                # Close short position if short EMA crosses above long EMA or RSI goes oversold
                if self.position.is_short and (crossover(self.short_ema, self.long_ema) or self.rsi[-1] < self.rsi_buy_level):
                     self.position.close()

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
    logger = logging.getLogger(__name__)

    data_dict = {}

    # Check if path is a directory or a single file
    if os.path.isdir(filepath):
        logger.info(f"Searching for CSV files in directory and subdirectories: {filepath}")

        # Walk through the directory and find all CSV files
        found_files = []
        for root, _, files in os.walk(filepath):
            for file in files:
                if file.endswith('.csv'):
                    found_files.append(os.path.join(root, file))

        if not found_files:
            logger.error(f"No CSV files found in directory or subdirectories: {filepath}")
            raise FileNotFoundError(f"No CSV files found in directory or subdirectories: {filepath}")

        logger.info(f"Found {len(found_files)} files: {', '.join([os.path.basename(f) for f in found_files])}")

        # Load each CSV file
        for file_path in found_files:
            try:
                # Extract asset and timeframe from filename using corrected regex
                match = re.search(r'([A-Z]+)_([0-9]+[mhd])_.*\.csv', os.path.basename(file_path))
                if match:
                    asset, timeframe_str = match.groups()
                    # Convert timeframe string to consistent format (e.g., '1d' to '1D')
                    timeframe = timeframe_str.replace('d', 'D').replace('h', 'h').replace('m', 'm') # Ensure consistent format
                    key = (asset, timeframe)
                    logger.info(f"Parsed asset='{asset}', timeframe='{timeframe}' from {os.path.basename(file_path)}")
                else:
                    key = ('UNKNOWN', 'UNKNOWN') # Default if parsing fails
                    logger.warning(f"Could not parse asset and timeframe from filename: {os.path.basename(file_path)}. Using default {key}.")

                logger.info(f"Loading data from: {file_path}")

                df = pd.read_csv(file_path, index_col='Date', parse_dates=True)

                # Convert numeric columns, handling potential commas or errors
                numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
                for column in numeric_columns:
                    if column in df.columns:
                         if df[column].dtype == 'object':
                            df[column] = df[column].astype(str).str.replace(',', '')
                         df[column] = pd.to_numeric(df[column], errors='coerce')

                df = df.dropna() # Drop rows with NaN values

                if not df.empty:
                     data_dict[key] = df
                     logger.info(f"Successfully loaded and processed {len(df)} rows from {os.path.basename(file_path)}.")
                else:
                    logger.warning(f"Processed DataFrame is empty for {os.path.basename(file_path)}. Skipping.")

            except Exception as e:
                logger.error(f"Error loading or processing {os.path.basename(file_path)}: {str(e)}")
                continue # Continue to the next file even if one fails

        if not data_dict:
            error_msg = f"No valid data could be loaded from any CSV file in {filepath} or its subdirectories."
            logger.error(error_msg)
            raise ValueError(error_msg)

        return data_dict

    elif os.path.isfile(filepath):
        # Handle single file loading
        logger.info(f"Loading single file: {filepath}")
        try:
            data = pd.read_csv(filepath, index_col='Date', parse_dates=True)

            numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            for column in numeric_columns:
                if column in data.columns:
                    if data[column].dtype == 'object':
                        data[column] = data[column].astype(str).str.replace(',', '')
                    data[column] = pd.to_numeric(data[column], errors='coerce')

            data = data.dropna() # Drop rows with NaN values

            if data.empty:
                error_msg = f"Processed DataFrame is empty for {filepath}."
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(f"Successfully loaded and processed {len(data)} rows from {filepath}.")

            # Try to infer asset/timeframe from filename for single file using corrected regex
            try:
                 match = re.search(r'([A-Z]+)_([0-9]+[mhd])', os.path.basename(filepath))
                 if match:
                     asset, timeframe_str = match.groups()
                     timeframe = timeframe_str.replace('d', 'D').replace('h', 'h').replace('m', 'm') # Ensure consistent format
                     key = (asset, timeframe)
                     logger.info(f"Inferred asset='{asset}', timeframe='{timeframe}' from filename.")
                 else:
                     key = ('SINGLE', '1D') # Default if inference fails
                     logger.warning(f"Could not infer asset and timeframe from single filename: {filepath}. Using default {key}.")
            except Exception as name_e:
                 logger.warning(f"Error inferring asset/timeframe from filename {filepath}: {str(name_e)}. Using default {key}.")
                 key = ('SINGLE', '1D')

            return {key: data}

        except Exception as e:
            logger.error(f"Error loading or processing single file {filepath}: {str(e)}")
            raise # Re-raise the exception

    else:
        logger.error(f"Invalid filepath: {filepath}. Path is neither a file nor a directory.")
        raise FileNotFoundError(f"Invalid filepath: {filepath}")

def run_backtest(data, cash=1000000, commission=0.002):
    """
    Run the backtest for the strategy.

    Args:
        data (pd.DataFrame): Preprocessed data
        cash (float): Initial cash
        commission (float): Commission per trade

    Returns:
        dict: Backtest results
    """
    # Note: basic_backtest.py had position sizing based on avg_price, removed for generality
    bt = Backtest(data, BullBearEMARsiScalping, cash=cash, commission=commission)
    results = bt.run()
    # Disable plotting by default as in basic_backtest.py
    # bt.plot()
    return results

def save_results(results, output_dir, filename="backtest_results.json"):
    """
    Saves backtest results to a JSON file.

    Args:
        results (dict): The backtest results dictionary.
        output_dir (str): The directory to save the results file.
        filename (str): The name of the results file.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logging.info(f"Created results directory: {output_dir}")

    filepath = os.path.join(output_dir, filename)
    try:
        # Convert results to a JSON serializable format
        # backtesting.py results object is a pandas Series, convert to dict
        results_dict = results.to_dict() if hasattr(results, 'to_dict') else results

        # Convert Timestamp objects to strings for JSON serialization
        for key, value in results_dict.items():
            if isinstance(value, pd.Timestamp):
                results_dict[key] = value.isoformat() # Convert to ISO format string
            # Handle Timedelta objects
            elif isinstance(value, pd.Timedelta):
                results_dict[key] = str(value) # Convert Timedelta to string
            # Handle NaN values
            elif isinstance(value, float) and pd.isna(value):
                results_dict[key] = None # Represent NaN as null in JSON

        with open(filepath, 'w') as f:
            json.dump(results_dict, f, indent=4)
        logging.info(f"Backtest results saved to: {filepath}")
    except Exception as e:
        logging.error(f"Error saving results to {filepath}: {str(e)}")
