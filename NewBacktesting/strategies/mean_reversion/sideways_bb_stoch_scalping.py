import os
import json
import logging
import re
import datetime
import pandas as pd
import talib # Use talib for consistency with basic_backtest.py

from backtesting import Backtest, Strategy
from backtesting.lib import crossover # Keep crossover if used in strategy logic

# Configure basic logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SidewaysBbStochScalping(Strategy):
    """
    Sideways Market Scalping Strategy using Bollinger Bands and Stochastic Oscillator.

    Entry Rules:
    - Buy: Price touches lower Bollinger Band and Stochastic K is oversold.
    - Sell: Price touches upper Bollinger Band and Stochastic K is overbought.

    Exit Rules:
    - Close long position when price approaches the middle band.
    - Close short position when price approaches the middle band.
    """
    # Define parameters for the strategy
    bb_length = 20
    bb_std = 2
    stoch_k = 14
    stoch_d = 3
    stoch_smooth_k = 3
    stoch_lower = 20
    stoch_upper = 80

    def init(self):
        self.logger = logging.getLogger(__name__)
        try:
            # Calculate Bollinger Bands and Stochastic Oscillator using talib
            close = self.data.Close
            high = self.data.High
            low = self.data.Low

            # TALIB BBANDS returns upperband, middleband, lowerband
            self.upper_band, self.middle_band, self.lower_band = self.I(talib.BBANDS, close, timeperiod=self.bb_length, nbdevup=self.bb_std, nbdevdn=self.bb_std) # Using SMA as MA type

            # TALIB STOCH returns slowk, slowd
            self.stoch_k_line, self.stoch_d_line = self.I(talib.STOCH, high, low, close,
                                                           fastk_period=self.stoch_k,
                                                           slowk_period=self.stoch_smooth_k, # smooth_k corresponds to slowk_period in talib
                                                           slowd_period=self.stoch_d)
            self.logger.info("Strategy initialized successfully")
        except Exception as e:
            self.logger.error(f"Error in init(): {str(e)}")
            raise

    def next(self):
        try:
            current_price = self.data.Close[-1]

            # Entry conditions
            if not self.position:
                # Buy condition: Price touches lower BB and Stochastic is oversold
                if current_price <= self.lower_band[-1] and self.stoch_k_line[-1] < self.stoch_lower:
                    self.buy()

                # Sell condition: Price touches upper BB and Stochastic is overbought
                elif current_price >= self.upper_band[-1] and self.stoch_k_line[-1] > self.stoch_upper:
                    self.sell()

            # Exit conditions (close positions when price approaches the middle band)
            else:
                if self.position.is_long and current_price >= self.middle_band[-1]:
                     self.position.close()
                if self.position.is_short and current_price <= self.middle_band[-1]:
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
    bt = Backtest(data, SidewaysBbStochScalping, cash=cash, commission=commission)
    results = bt.run()
    # Disable plotting by default
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
