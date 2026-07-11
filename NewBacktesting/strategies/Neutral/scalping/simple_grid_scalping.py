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

class SimpleGridScalping(Strategy):
    # Define parameters for the strategy
    ema_period = 20 # Period for the central EMA
    grid_spacing_pct = 0.1 # Percentage difference for grid levels (e.g., 0.1 means 0.1%)
    num_levels = 5 # Number of grid levels above and below the EMA
    stop_loss_pct = None # Percentage below entry price to set stop loss (e.g., 1.0 for 1%) - None to disable
    take_profit_pct = None # Percentage above entry price to set take profit (e.g., 1.0 for 1%) - None to disable

    def init(self):
        self.logger = logging.getLogger(__name__)
        try:
            # Calculate the central EMA using talib
            close = self.data.Close
            self.ema = self.I(talib.EMA, close, timeperiod=self.ema_period)
            self.buy_levels = []
            self.sell_levels = []
            self.logger.info("Strategy initialized successfully")
        except Exception as e:
            self.logger.error(f"Error in init(): {str(e)}")
            raise

    def next(self):
        try:
            current_price = self.data.Close[-1]
            central_price = self.ema[-1]

            # Calculate buy and sell levels based on the central price and grid spacing
            # Re-calculate levels if price moves significantly or initially set
            if not self.buy_levels or abs(current_price - self.buy_levels[0]) > central_price * (self.grid_spacing_pct / 100) * 0.5:
                 self.buy_levels = sorted([central_price * (1 - (i + 1) * self.grid_spacing_pct / 100) for i in range(self.num_levels)], reverse=True)
                 self.sell_levels = sorted([central_price * (1 + (i + 1) * self.grid_spacing_pct / 100) for i in range(self.num_levels)])
                 # Ensure levels are sorted for easier iteration if needed, though not strictly necessary for this logic

            # Place buy orders at the calculated buy levels
            # Iterate through levels from highest to lowest for buys to potentially catch price dips sequentially
            for level in self.buy_levels:
                 # Check if current price is at or below the buy level and we are not currently long
                 if current_price <= level and not self.position.is_long:
                     # Calculate SL and TP prices based on entry price if parameters are set
                     sl_price = level * (1 - self.stop_loss_pct / 100) if self.stop_loss_pct is not None else None
                     tp_price = level * (1 + self.take_profit_pct / 100) if self.take_profit_pct is not None else None

                     self.buy(sl=sl_price, tp=tp_price)
                     self.logger.info(f"Buy order placed at {level:.2f} (current price {current_price:.2f})")
                     if sl_price is not None: self.logger.info(f"  Stop Loss set at {sl_price:.2f}")
                     if tp_price is not None: self.logger.info(f"  Take Profit set at {tp_price:.2f}")
                     # In a real grid strategy, you might manage multiple open orders/positions.
                     # This simple example assumes only one position is managed at a time.
                     break # Execute only one buy at the highest triggered level below current price

            # Place sell orders (or close long positions) at the calculated sell levels
            # Iterate through levels from lowest to highest for sells to potentially take profit sequentially
            for level in self.sell_levels:
                 # Check if current price is at or above the sell level and we are currently long
                 if current_price >= level and self.position.is_long:
                     self.position.close()
                     self.logger.info(f"Closed long position at {current_price:.2f} (sell level {level:.2f})")
                     # In a real grid strategy, you might manage multiple open orders/positions.
                     # This simple example assumes only one position is managed at a time.
                     break # Exit at the lowest triggered level above current price

            # Optional: Add logic for closing short positions if implementing shorting
            # if self.position.is_short:
            #    # Add logic to close short position, e.g., when price moves below a level
            #    pass

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
                # Updated regex to match filenames like ASSET_TIMEFRAME_NUMBERcandles_DATE.csv
                match = re.search(r'([A-Z]+)_([0-9]+[mhd])_\d+candles_\d{8}\.csv', os.path.basename(file_path))
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
                # Updated regex to match filename like ASSET_TIMEFRAME_NUMBERcandles_DATE.csv
                match = re.search(r'([A-Z]+)_([0-9]+[mhd])_\d+candles_\d{8}\.csv', os.path.basename(filepath))
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
    bt = Backtest(data, SimpleGridScalping, cash=cash, commission=commission)
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
        # Convert results to a JSON serializable format, explicitly excluding non-serializable objects
        # backtesting.py results object is a pandas Series, convert to dict
        results_dict = results.to_dict() if hasattr(results, 'to_dict') else results

        # Remove non-serializable items if they exist (like the strategy object reference)
        if '_strategy' in results_dict:
            del results_dict['_strategy']

        if '_equity_curve' in results_dict:
            # Convert equity curve DataFrame to a serializable format, e.g., list of dicts
            results_dict['_equity_curve'] = results_dict['_equity_curve'].reset_index().to_dict(orient='records')

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

# Notes for Further Advancement:
# 1. Implement a more sophisticated grid management system (e.g., multiple open orders, partial fills).
# 2. Add dynamic grid spacing based on volatility.
# 3. Incorporate stop losses and take profits for individual grid trades.
# 4. Consider adding trend filters to avoid trading against strong trends.
# 5. Add volume confirmation for entries.
