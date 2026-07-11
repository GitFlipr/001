import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover, plot_heatmaps
import matplotlib.pyplot as plt

class VolatilityBreakoutATRStrategy(Strategy):
    """
    ATR-based Volatility Breakout Strategy
    
    This strategy enters long positions when price breaks above the ATR-based upper band
    and enters short positions when price breaks below the ATR-based lower band.
    
    Parameters:
    -----------
    atr_period : int
        The period for calculating the Average True Range (ATR)
    atr_multiplier : float
        Multiplier for ATR to set breakout bands
    stop_loss_atr : float
        ATR multiplier for stop loss distance
    take_profit_atr : float
        ATR multiplier for take profit distance (0 to disable)
    risk_percent : float
        Percentage of account to risk per trade (0.01 = 1%)
    lookback_period : int
        Number of bars to look back for setting breakout levels
    """
    # Strategy parameters (optimizable)
    atr_period = 14
    atr_multiplier = 1.5
    stop_loss_atr = 1.0
    take_profit_atr = 2.0  # 0 to disable take profit
    risk_percent = 0.02  # Risk 2% of account per trade
    lookback_period = 20  # Period for setting breakout levels
    
    def init(self):
        """Initialize indicators and strategy components"""
        # Calculate ATR more efficiently using the built-in indicator
        self.atr = self.I(self.compute_atr, self.data.High, self.data.Low, self.data.Close, self.atr_period)
        
        # Use a more responsive method for calculating breakout levels
        # This uses rolling highs/lows plus ATR instead of just current price + ATR
        price = self.data.Close
        high = self.data.High
        low = self.data.Low
        
        # Calculate rolling highs and lows for breakout levels
        rolling_high = self.I(lambda: pd.Series(high).rolling(self.lookback_period).max())
        rolling_low = self.I(lambda: pd.Series(low).rolling(self.lookback_period).min())
        
        # Define breakout levels based on rolling highs/lows + ATR
        self.upper_band = self.I(lambda: rolling_high + self.atr * self.atr_multiplier)
        self.lower_band = self.I(lambda: rolling_low - self.atr * self.atr_multiplier)
        
        # Plot the indicators - remove unsupported parameters like 'width'
        self.I(lambda: self.upper_band, overlay=True, color='green')
        self.I(lambda: self.lower_band, overlay=True, color='red')
        self.I(lambda: self.atr, name='ATR')
        
        # For debugging
        self.trade_dates = []
        self.trade_prices = []
        self.trade_types = []

    def compute_atr(self, high, low, close, period):
        """
        Calculate ATR (Average True Range)
        
        Parameters:
        -----------
        high : Series
            High prices
        low : Series
            Low prices
        close : Series
            Close prices
        period : int
            ATR calculation period
            
        Returns:
        --------
        Series
            ATR values
        """
        tr1 = high - low
        tr2 = np.abs(high - np.roll(close, 1))
        tr3 = np.abs(low - np.roll(close, 1))
        tr2[0] = tr3[0] = 0  # Set first value to avoid lookback error
        
        tr = np.maximum(tr1, np.maximum(tr2, tr3))
        atr = pd.Series(tr).ewm(span=period, adjust=False).mean()
        return atr

    def next(self):
        """Define trading logic to execute on each candle"""
        price = self.data.Close[-1]
        
        # Skip initial bars until indicators are warmed up
        if len(self.data) <= self.lookback_period:
            return
        
        # Calculate position size based on risk
        if self.stop_loss_atr > 0:
            stop_distance = self.atr[-1] * self.stop_loss_atr
            if stop_distance > 0:  # Prevent division by zero
                risk_amount = self.equity * self.risk_percent
                position_size = risk_amount / stop_distance
            else:
                position_size = 1.0  # Default if unable to calculate
        else:
            position_size = 1.0  # Default position size
            stop_distance = 0
        
        # Entry conditions
        if not self.position:  # If not in a position
            # Long entry - price closed above upper band
            if self.data.Close[-1] > self.upper_band[-1] and self.data.Close[-2] <= self.upper_band[-2]:
                sl_price = price - stop_distance if self.stop_loss_atr > 0 else None
                tp_price = price + (self.atr[-1] * self.take_profit_atr) if self.take_profit_atr > 0 else None
                self.buy(size=position_size, sl=sl_price, tp=tp_price)
                
                # For debugging
                self.trade_dates.append(self.data.index[-1])
                self.trade_prices.append(price)
                self.trade_types.append('BUY')
                
            # Short entry - price closed below lower band
            elif self.data.Close[-1] < self.lower_band[-1] and self.data.Close[-2] >= self.lower_band[-2]:
                sl_price = price + stop_distance if self.stop_loss_atr > 0 else None
                tp_price = price - (self.atr[-1] * self.take_profit_atr) if self.take_profit_atr > 0 else None
                self.sell(size=position_size, sl=sl_price, tp=tp_price)
                
                # For debugging
                self.trade_dates.append(self.data.index[-1])
                self.trade_prices.append(price)
                self.trade_types.append('SELL')
        
        # Exit conditions (in addition to SL/TP)
        else:
            # Exit long position if price closes below middle band
            if self.position.is_long and self.data.Close[-1] < (self.upper_band[-1] + self.lower_band[-1]) / 2:
                self.position.close()
                
                # For debugging
                self.trade_dates.append(self.data.index[-1])
                self.trade_prices.append(price)
                self.trade_types.append('CLOSE LONG')
                
            # Exit short position if price closes above middle band
            elif self.position.is_short and self.data.Close[-1] > (self.upper_band[-1] + self.lower_band[-1]) / 2:
                self.position.close()
                
                # For debugging
                self.trade_dates.append(self.data.index[-1])
                self.trade_prices.append(price)
                self.trade_types.append('CLOSE SHORT')


def evaluate_strategy(data, params=None, plot=True):
    """
    Evaluate the strategy with given parameters
    
    Parameters:
    -----------
    data : DataFrame
        OHLC price data
    params : dict
        Strategy parameters to override defaults
    plot : bool
        Whether to generate plots
        
    Returns:
    --------
    dict
        Performance statistics
    """
    strategy_params = {}
    if params:
        strategy_params = params
    
    # Use a reasonable cash value based on the asset price
    initial_cash = 10000
    
    bt = Backtest(data, VolatilityBreakoutATRStrategy, cash=initial_cash, commission=0.001, 
                  exclusive_orders=True, trade_on_close=False)
    
    stats = bt.run(**strategy_params)
    
    if plot:
        try:
            # Handle warning about too many candlesticks by setting resample parameter
            bt.plot(filename="atr_strategy_results.html", open_browser=False, resample='4h')
        except Exception as e:
            print(f"Warning: Could not generate plot: {str(e)}")
        
        # Print key metrics (using proper key names with brackets and %)
        print("\nKey Performance Metrics:")
        try:
            print(f"Return: {stats['Return [%]']:.2f}%")
            print(f"Sharpe Ratio: {stats['Sharpe Ratio']:.2f}")
            print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
            print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
            print(f"Profit Factor: {stats['Profit Factor']:.2f}")
            print(f"# Trades: {stats['# Trades']}")
        except KeyError as e:
            print(f"Error: Metric {e} not found in results.")
            print(f"Available metrics: {list(stats.index)}")
        
    return stats


def optimize_parameters(data):
    """
    Optimize strategy parameters
    
    Parameters:
    -----------
    data : DataFrame
        OHLC price data
        
    Returns:
    --------
    tuple
        (optimal parameters, optimization stats)
    """
    bt = Backtest(data, VolatilityBreakoutATRStrategy, cash=10000, commission=0.001)
    
    # Simplify optimization parameter space to avoid errors
    optimization_params = {
        'atr_period': range(10, 21, 5),          # [10, 15, 20]
        'atr_multiplier': [1.0, 1.5, 2.0],       # Simplified range
        'stop_loss_atr': [0.5, 1.0, 1.5],        # Simplified range
        'take_profit_atr': [1.0, 2.0, 3.0],      # Simplified range
        'lookback_period': [10, 20, 30]          # Added lookback period
    }
    
    try:
        print("Starting optimization (this may take a while)...")
        # Optimize for Sharpe ratio with no constraint to avoid broadcasting errors
        results = bt.optimize(**optimization_params, maximize='Sharpe Ratio')
        
        print("\nBest parameters found:")
        for param, value in results._strategy.items():
            print(f"{param}: {value}")
            
        # Print heatmap plots for parameter combinations
        try:
            if hasattr(bt, 'plot_heatmaps'):
                bt.plot_heatmaps(filename="atr_optimization_heatmaps.html", open_browser=False)
        except Exception as e:
            print(f"Warning: Could not generate heatmaps: {str(e)}")
            
        return results
    except Exception as e:
        print(f"Error during optimization: {str(e)}")
        # Return default parameters in case of error
        return {}


def load_sample_data():
    """
    Load DOGE data for testing
    
    Returns:
    --------
    DataFrame
        OHLC price data
    """
    # Load Dogecoin data from the specified directory
    data_path = r"C:\Users\MoonBots\Desktop\code\Backtesting\Data\coins\sol"
    
    try:
        # Try to find csv files in the directory
        import os
        import glob
        
        # Look for CSV files in the directory
        csv_files = glob.glob(os.path.join(data_path, "*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in configured data path: {data_path}")
        
        # Use the first CSV file found (or you can implement logic to select a specific file)
        file_path = csv_files[0]
        print(f"Loading data from: {file_path}")
        
        # Read the CSV file
        # Assuming standard OHLCV format, adjust parsing as needed for your specific files
        df = pd.read_csv(file_path)
        
        # Check if there's a date/timestamp column
        date_columns = [col for col in df.columns if 'date' in col.lower() or 'time' in col.lower()]
        
        if date_columns:
            # Set the first date column as index
            df = df.set_index(date_columns[0])
            print(f"Using date column: {date_columns[0]}")
        else:
            # If no obvious date column, try the first column
            print(f"No date column found, using first column: {df.columns[0]}")
            df = df.set_index(df.columns[0])
            
        # Make sure the index is datetime
        if not isinstance(df.index, pd.DatetimeIndex):
            print("Converting index to datetime")
            df.index = pd.to_datetime(df.index)
        
        # Based on the error output, we see that the file has lowercase column names
        # but we need proper capitalized column names for the strategy
        column_mapping = {
            'open': 'Open',
            'high': 'High', 
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        }
        
        # Apply mapping for columns that exist
        for old_col, new_col in column_mapping.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]
                print(f"Mapped column {old_col} to {new_col}")
            
        # Ensure we have all required columns
        required_columns = ['Open', 'High', 'Low', 'Close']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns in source CSV: {', '.join(missing_columns)}")
            
        df.sort_index(inplace=True)
        
        # Remove future data if the date extends beyond today
        today = pd.Timestamp.now()
        if df.index.max() > today:
            print(f"Removing future data beyond {today}")
            df = df[df.index <= today]
        
        # Use only 1 year of data for faster processing
        if len(df) > 20000:
            print(f"Dataset is very large ({len(df)} bars). Using the most recent year of data.")
            one_year_ago = today - pd.Timedelta(days=365)
            df = df[df.index >= one_year_ago]
        
        print(f"Successfully loaded DOGE data: {len(df)} bars from {df.index[0]} to {df.index[-1]}")
        return df
        
    except Exception as e:
        raise RuntimeError(f"Error loading source data: {e}") from e


def verify_data(data):
    """
    Verify data is suitable for backtesting
    
    Parameters:
    -----------
    data : DataFrame
        OHLC price data
        
    Returns:
    --------
    bool
        True if data is valid, False otherwise
    """
    print("\n=== Data Verification ===")
    
    # Check for price anomalies
    close_prices = data['Close']
    high_prices = data['High']
    low_prices = data['Low']
    
    # Calculate returns
    returns = close_prices.pct_change()
    
    print(f"Price range: {low_prices.min():.4f} to {high_prices.max():.4f}")
    print(f"Average daily return: {returns.mean()*100:.4f}%")
    print(f"Return volatility: {returns.std()*100:.4f}%")
    
    # Check for extreme price movements
    max_daily_return = returns.max() * 100
    min_daily_return = returns.min() * 100
    
    print(f"Max single-period return: {max_daily_return:.2f}%")
    print(f"Min single-period return: {min_daily_return:.2f}%")
    
    # Flag potential data issues
    issues_found = False
    
    if (high_prices < low_prices).any():
        print("WARNING: High prices less than low prices detected!")
        issues_found = True
        
    if (close_prices > high_prices).any() or (close_prices < low_prices).any():
        print("WARNING: Close prices outside of high-low range detected!")
        issues_found = True
        
    if returns.isnull().sum() > 0:
        print(f"WARNING: {returns.isnull().sum()} NaN values in returns!")
        issues_found = True
        
    if max_daily_return > 50 or min_daily_return < -50:
        print("WARNING: Extreme price movements detected (>50%)!")
        issues_found = True
    
    if not issues_found:
        print("No obvious data issues detected.")
        
    return not issues_found
