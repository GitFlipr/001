import os
import json
import logging
import re
import datetime
import pandas as pd
import numpy as np
import talib # Use talib for consistency with basic_backtest.py

from backtesting import Backtest, Strategy
# No specific lib functions needed for this strategy currently

# Configure basic logging if not already configured
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LowVolatilityBbAdxScalping(Strategy):
    """
    Low Volatility Scalping Strategy using Bollinger Bands Squeeze and ADX.

    Entry Rules:
    - Buy: Price breaks above upper Bollinger Band after a squeeze and ADX indicates low volatility.

    Exit Rules:
    - Close position if price drops below the middle or lower Bollinger Band.
    """
    # Define parameters for the strategy
    bb_length = 20
    bb_std = 2
    adx_length = 14
    adx_threshold = 20 # ADX value to indicate low volatility
    squeeze_lookback = 10 # Bars to check for BB squeeze

    def init(self):
        self.logger = logging.getLogger(__name__)
        try:
            # Calculate Bollinger Bands and ADX using talib
            close = self.data.Close
            high = self.data.High
            low = self.data.Low

            # TALIB BBANDS returns upperband, middleband, lowerband
            self.upper_band, self.middle_band, self.lower_band = self.I(talib.BBANDS, close, timeperiod=self.bb_length, nbdevup=self.bb_std, nbdevdn=self.bb_std) # Using SMA as MA type

            # Calculate Bollinger Band Width for squeeze detection
            self.bb_width = self.I(self._bb_width, self.upper_band, self.middle_band, self.lower_band) # Calculate percentage width

            # TALIB ADX returns adx
            self.adx = self.I(talib.ADX, high, low, close, timeperiod=self.adx_length)

            self.logger.info("Strategy initialized successfully")
        except Exception as e:
            self.logger.error(f"Error in init(): {str(e)}")
            raise

    @staticmethod
    def _bb_width(upper, middle, lower):
        upper = np.asarray(upper, dtype=float)
        middle = np.asarray(middle, dtype=float)
        lower = np.asarray(lower, dtype=float)
        return np.where(np.abs(middle) > 1e-12, (upper - lower) / middle, 0.0)

    def next(self):
        try:
            current_price = self.data.Close[-1]

            # Detect Bollinger Band Squeeze (simplified: check if current width is low relative to recent history)
            is_squeeze = False
            if len(self.bb_width) > self.squeeze_lookback:
                 recent_bb_widths = self.bb_width[-self.squeeze_lookback-1:-1]
                 if self.bb_width[-1] < recent_bb_widths.mean(): # Current width is below average of recent widths
                      is_squeeze = True

            # Entry condition: Price breaks above upper BB after a squeeze and ADX indicates low volatility
            # Note: ADX < 20 is a common interpretation for low trend/volatility
            if not self.position:
                 if is_squeeze and current_price > self.upper_band[-1] and self.adx[-1] < self.adx_threshold:
                     # Calculate stop loss just below the breakout level (e.g., the upper band before breakout)
                     # Using the previous upper band value or a percentage below entry
                     stop_loss = self.upper_band[-2] if len(self.upper_band) > 1 else current_price * 0.99 # Fallback stop loss
                     self.buy(sl=stop_loss)
                     self.logger.info(f"Long entry at {current_price:.2f}, SL: {stop_loss:.2f}")

            # Exit condition: Close position if price drops below the middle band or lower band
            else:
                if self.position.is_long and (current_price < self.middle_band[-1] or current_price < self.lower_band[-1]):
                     self.position.close()
                     self.logger.info(f"Closed long position at {current_price:.2f}")

        except Exception as e:
            self.logger.error(f"Error in next(): {str(e)}")
            raise

# Include load_data, run_backtest, save_results functions and __main__ block
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
    bt = Backtest(data, LowVolatilityBbAdxScalping, cash=cash, commission=commission)
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
