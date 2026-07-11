import pandas as pd
import numpy as np
import pandas_ta as ta
import matplotlib.pyplot as plt
import seaborn as sns 
import os
import glob
from datetime import datetime
import matplotlib
# Set matplotlib to use a non-interactive backend to avoid hanging
matplotlib.use('Agg')

class Backtesting:
    def __init__(self,
                 data_file=None,
                 data_dir=None,
                 ema_period=20,
                 bb_period=20,
                 bb_std=2,
                 rsi_period=14,
                 min_profit_target=0.01,
                 max_profit_target=0.10,
                 trailing_stop_loss=0.02,
                 risk_free_rate=0.02,
                 scalping_window=5,  # Window size for scalping signals
                 volume_threshold=1.5,  # Volume threshold multiplier
                 rsi_buy_threshold=60,  # RSI threshold for buying (try 30)
                 rsi_sell_threshold=40,  # RSI threshold for selling (try 70)
                 atr_period=14,  # ATR period for volatility-based position sizing
                 trend_ema_period=50,  # Longer period for trend detection
                 regime_ema_period=200,  # Very long period for market regime
                 max_position_size=1.0,  # Maximum position size as fraction of capital
                 min_position_size=0.1,  # Minimum position size
                 volatility_threshold=0.02):  # Volatility threshold for position sizing
        """
        Enhanced Backtesting class with improved strategy features.

        Parameters:
        :param data_file: Path to a single data file for backtesting
        :param data_dir: Path to a directory containing multiple data files
        :param ema_period: Period for EMA calculation
        :param bb_period: Period for Bollinger Bands calculation
        :param bb_std: Standard deviation for Bollinger Bands
        :param rsi_period: Period for RSI calculation
        :param min_profit_target: Minimum profit target for trade exit
        :param max_profit_target: Maximum profit target for trade exit
        :param trailing_stop_loss: Trailing stop loss percentage
        :param risk_free_rate: Risk-free rate for performance metrics
        :param scalping_window: Rolling window size for short-term price action
        :param volume_threshold: Multiplier for volume spike detection
        :param rsi_buy_threshold: RSI threshold for buy signals (higher means less strict)
        :param rsi_sell_threshold: RSI threshold for sell signals (lower means less strict)
        :param atr_period: ATR period for volatility measurement
        :param trend_ema_period: Longer period for trend detection
        :param regime_ema_period: Very long period for market regime
        :param max_position_size: Maximum position size as fraction of capital
        :param min_position_size: Minimum position size
        :param volatility_threshold: Volatility threshold for position sizing
        """
        self.data_file = data_file
        self.data_dir = data_dir
        self.ema_period = ema_period
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.min_profit_target = min_profit_target
        self.max_profit_target = max_profit_target
        self.trailing_stop_loss = trailing_stop_loss
        self.risk_free_rate = risk_free_rate
        self.scalping_window = scalping_window
        self.volume_threshold = volume_threshold
        self.rsi_buy_threshold = rsi_buy_threshold
        self.rsi_sell_threshold = rsi_sell_threshold
        
        # New parameters
        self.atr_period = atr_period
        self.trend_ema_period = trend_ema_period
        self.regime_ema_period = regime_ema_period
        self.max_position_size = max_position_size
        self.min_position_size = min_position_size
        self.volatility_threshold = volatility_threshold
        
        # Column name mappings to handle different data formats
        self.column_mappings = {
            'date': ['date', 'time', 'datetime', 'timestamp', 'Date', 'Time', 'DateTime', 'Timestamp'],
            'open': ['open', 'Open', 'OPEN', 'o', 'O'],
            'high': ['high', 'High', 'HIGH', 'h', 'H'],
            'low': ['low', 'Low', 'LOW', 'l', 'L'],
            'close': ['close', 'Close', 'CLOSE', 'adj close', 'Adj Close', 'ADJ CLOSE', 'Last', 'last', 'LAST', 'price', 'Price', 'PRICE', 'c', 'C'],
            'volume': ['volume', 'Volume', 'VOLUME', 'vol', 'Vol', 'v', 'V']
        }
        
        if self.data_file:
            self.data = self._load_data(self.data_file)
            if self.data is not None and len(self.data) > 0:
                self._calculate_indicators()
                self._add_scalping_indicators()
        elif self.data_dir:
            self.file_results = self.process_directory()
        else:
            raise ValueError("Either data_file or data_dir must be provided")

    def _load_data(self, file_path):
        """
        Load historical data from a file with flexible column mapping.
        Handles various file formats and column naming conventions.
        
        :param file_path: Path to the data file
        :return: Processed DataFrame
        """
        try:
            print(f"Loading data from {file_path}...")
            
            # Load data based on file extension
            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                data = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                data = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format for {file_path}. Please use CSV, Excel, or JSON.")
            
            # Print data structure for debugging
            print(f"File contains {len(data)} rows and columns: {data.columns.tolist()}")
            
            # Map columns based on available headers
            # Find date column
            date_col = None
            for possible_name in self.column_mappings['date']:
                if possible_name in data.columns:
                    date_col = possible_name
                    break
            
            if date_col is None:
                print(f"Warning: No date column found in {file_path}. Creating a synthetic date index.")
                # If no date column found, create one using the index
                data['datetime'] = pd.date_range(start=datetime.now().replace(hour=0, minute=0, second=0), 
                                               periods=len(data), 
                                               freq='D')
                date_col = 'datetime'
            else:
                print(f"Using '{date_col}' as the date column.")
            
            # Convert date to datetime
            data['datetime'] = pd.to_datetime(data[date_col], errors='coerce')
            data.set_index('datetime', inplace=True)
            
            # Map price columns
            for target, possible_names in self.column_mappings.items():
                if target == 'date':  # Skip date, already handled
                    continue
                    
                # Find the first matching column
                found = False
                for name in possible_names:
                    if name in data.columns:
                        data[target] = pd.to_numeric(data[name], errors='coerce')
                        print(f"Mapped '{name}' to '{target}'")
                        found = True
                        break
                
                if not found and target == 'close':
                    # Special handling for close price - very important
                    for col in data.columns:
                        if any(price_term in col.lower() for price_term in ['price', 'close', 'last', 'value']):
                            data['close'] = pd.to_numeric(data[col], errors='coerce')
                            print(f"Mapped '{col}' to 'close' based on name pattern")
                            found = True
                            break
            
            # Handle missing required columns
            if 'close' not in data.columns:
                # If we have other price columns, derive close from them
                if 'open' in data.columns and 'high' in data.columns and 'low' in data.columns:
                    data['close'] = (data['open'] + data['high'] + data['low']) / 3
                    print("Created 'close' as average of open, high, and low")
                else:
                    # Last resort - take any numeric column
                    for col in data.columns:
                        try:
                            values = pd.to_numeric(data[col], errors='coerce')
                            if not values.isna().all() and values.std() > 0:
                                data['close'] = values
                                print(f"Using '{col}' as 'close' price (last resort)")
                                break
                        except:
                            continue
                    
                    # If still no close price found, cannot proceed
                    if 'close' not in data.columns:
                        raise ValueError(f"Could not identify or derive close price column in {file_path}")
            
            # If volume not found, create a dummy one
            if 'volume' not in data.columns:
                print(f"Warning: No volume data found in {file_path}. Using placeholder values.")
                # Create increasing volume as placeholder
                data['volume'] = range(1000, 1000 + len(data))
            
            # Remove NaN values
            initial_length = len(data)
            data = data.dropna(subset=['close'])
            if len(data) < initial_length:
                print(f"Removed {initial_length - len(data)} rows with NaN close values")
            
            # Print data summary
            print(f"Final data shape: {data.shape}")
            print(f"Date range: {data.index.min()} to {data.index.max()}")
            print(f"Close price range: {data['close'].min()} to {data['close'].max()}")
            
            return data
            
        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")
            return None

    def _calculate_indicators(self):
        """
        Calculate technical indicators required for the strategy.
        """
        # Ensure data is available
        if self.data is None or len(self.data) == 0:
            raise ValueError("No data available for calculating indicators")
            
        # Add technical indicators
        try:
            # EMA
            self.data['EMA'] = ta.ema(self.data['close'], length=self.ema_period)
            
            # Bollinger Bands
            bollinger = ta.bbands(self.data['close'], length=self.bb_period, std=self.bb_std)
            self.data = pd.concat([self.data, bollinger], axis=1)
            
            # RSI
            self.data['RSI'] = ta.rsi(self.data['close'], length=self.rsi_period)
            
            # MACD
            macd = ta.macd(self.data['close'])
            self.data = pd.concat([self.data, macd], axis=1)
            
            # ATR for volatility measurement
            self.data['ATR'] = ta.atr(self.data['high'], self.data['low'], self.data['close'], length=self.atr_period)
            
            # Trend EMAs
            self.data['Trend_EMA'] = ta.ema(self.data['close'], length=self.trend_ema_period)
            self.data['Regime_EMA'] = ta.ema(self.data['close'], length=self.regime_ema_period)
            
            # Market regime detection
            self.data['Regime'] = np.where(self.data['close'] > self.data['Regime_EMA'], 1, -1)
            
            # Volatility bands
            self.data['Volatility_Upper'] = self.data['close'] * (1 + self.data['ATR'] / self.data['close'])
            self.data['Volatility_Lower'] = self.data['close'] * (1 - self.data['ATR'] / self.data['close'])
            
            # Replace NaN values with forward fill then backward fill
            self.data = self.data.fillna(method='ffill').fillna(method='bfill')
            
            # Check if any columns are still NaN
            nan_cols = self.data.columns[self.data.isna().any()].tolist()
            if nan_cols:
                print(f"Warning: The following columns still contain NaN values after filling: {nan_cols}")
                # Fill remaining NaN with 0
                self.data = self.data.fillna(0)
            
        except Exception as e:
            print(f"Error calculating indicators: {str(e)}")
            raise

    def process_directory(self):
        """
        Process all supported files in the directory.
        
        :return: Dictionary with results for each file
        """
        if not os.path.isdir(self.data_dir):
            raise ValueError(f"Directory not found: {self.data_dir}")
            
        results = {}
        
        # Get all data files with supported extensions
        file_patterns = [
            os.path.join(self.data_dir, "*.csv"),
            os.path.join(self.data_dir, "*.xlsx"),
            os.path.join(self.data_dir, "*.xls"),
            os.path.join(self.data_dir, "*.json")
        ]
        
        all_files = []
        for pattern in file_patterns:
            all_files.extend(glob.glob(pattern))
        
        if not all_files:
            print(f"No supported data files found in {self.data_dir}")
            return results
        
        print(f"Found {len(all_files)} files to process: {[os.path.basename(f) for f in all_files]}")
            
        # Process each file
        for file_path in all_files:
            try:
                print(f"\n{'='*50}")
                print(f"Processing {os.path.basename(file_path)}...")
                print(f"{'='*50}")
                
                self.data = self._load_data(file_path)
                
                if self.data is not None and len(self.data) > 0:
                    self._calculate_indicators()
                    self._add_scalping_indicators()
                    self.backtest()
                    performance, trades, equity_curve = self.calculate_performance()
                    
                    results[os.path.basename(file_path)] = {
                        'performance': performance,
                        'trades': trades,
                        'equity_curve': equity_curve
                    }
                    
                    print(f"Completed backtest for {os.path.basename(file_path)}.")
                    self._print_performance_summary(performance)
                    
                    # Save individual results
                    results_dir = os.path.join(self.data_dir, 'results')
                    os.makedirs(results_dir, exist_ok=True)
                    
                    # Save plot to file
                    self.plot_results(
                        file_name=os.path.join(results_dir, os.path.basename(file_path).split('.')[0]),
                        show_plot=False
                    )
                else:
                    print(f"Skipping {os.path.basename(file_path)} - failed to load data")
                    
            except Exception as e:
                print(f"Error processing {os.path.basename(file_path)}: {str(e)}")
                import traceback
                traceback.print_exc()
                results[os.path.basename(file_path)] = {'error': str(e)}
                
        return results

    def _add_scalping_indicators(self):
        """
        Add scalping-specific indicators to the dataset.
        """
        # Price momentum
        self.data['price_change'] = self.data['close'].pct_change()
        self.data['momentum'] = self.data['close'].diff(periods=self.scalping_window)
        
        # Volume analysis
        self.data['volume_ma'] = self.data['volume'].rolling(window=self.scalping_window).mean()
        self.data['volume_ratio'] = self.data['volume'] / self.data['volume_ma']
        
        # Price volatility
        self.data['volatility'] = self.data['close'].rolling(window=self.scalping_window).std()
        
        # Short-term trend
        self.data['short_ema'] = self.data['close'].ewm(span=self.scalping_window, adjust=False).mean()
        self.data['medium_ema'] = self.data['close'].ewm(span=self.scalping_window*2, adjust=False).mean()
        
        # Fill NaN values
        self.data = self.data.fillna(method='ffill').fillna(method='bfill').fillna(0)

    def _calculate_scalping_signals(self):
        """
        Calculate scalping-specific entry and exit signals.
        """
        # Volume spike detection - less strict condition
        volume_spike = self.data['volume_ratio'] > self.volume_threshold * 0.8  # 20% more lenient
        
        # Trend alignment 
        short_term_trend = self.data['short_ema'] > self.data['medium_ema']
        
        # Price momentum confirmation - allow smaller positive momentum
        positive_momentum = self.data['momentum'] > 0
        
        # Combine signals - less restrictive conditions
        self.data['scalp_buy_signal'] = (
            (volume_spike | (self.data['volume_ratio'] > 1.0)) &  # Less strict volume condition 
            (short_term_trend | (self.data['close'] > self.data['EMA'])) &  # Alternative trend condition
            (positive_momentum | (self.data['price_change'] > 0)) &  # Alternative momentum condition
            (self.data['RSI'] < 40)  # Not extremely overbought
        )
        
        self.data['scalp_sell_signal'] = (
            (self.data['RSI'] > 60) &  # Not extremely oversold
            ((~short_term_trend) | 
             (self.data['volume_ratio'] < 1.2) |  # Less strict volume decline
             (self.data['price_change'] < 0))  # Price declining
        )

    def _calculate_position_size(self, current_price, atr_value):
        """
        Calculate dynamic position size based on volatility.
        
        :param current_price: Current price
        :param atr_value: Current ATR value
        :return: Position size as fraction of capital
        """
        # Calculate volatility ratio
        volatility_ratio = atr_value / current_price
        
        # Adjust position size based on volatility
        if volatility_ratio > self.volatility_threshold:
            # Reduce position size in high volatility
            position_size = self.max_position_size * (self.volatility_threshold / volatility_ratio)
        else:
            # Use maximum position size in low volatility
            position_size = self.max_position_size
        
        # Ensure position size is within bounds
        position_size = max(self.min_position_size, min(self.max_position_size, position_size))
        
        return position_size

    def backtest(self):
        """
        Execute the backtest with enhanced strategy features.
        """
        self._calculate_scalping_signals()
        self.data['Signal'] = 0
        self.data['Entry_Price'] = np.nan
        self.data['Exit_Price'] = np.nan
        self.data['Trailing_Stop'] = np.nan
        self.data['Position_Size'] = np.nan

        in_position = False
        entry_price = 0
        max_price = 0
        trailing_stop = 0
        position_size = 0

        for i in range(max(self.scalping_window, self.regime_ema_period), len(self.data)):
            current_price = self.data['close'].iloc[i]
            current_atr = self.data['ATR'].iloc[i]
            
            # Calculate dynamic position size
            position_size = self._calculate_position_size(current_price, current_atr)
            
            # Market regime check
            current_regime = self.data['Regime'].iloc[i]
            trend_direction = 1 if self.data['close'].iloc[i] > self.data['Trend_EMA'].iloc[i] else -1
            
            # Enhanced buy condition
            buy_condition = (
                self.data['scalp_buy_signal'].iloc[i] and
                current_regime == 1 and  # Only buy in bullish regime
                trend_direction == 1 and  # Only buy in uptrend
                (
                    # Original condition with improvements
                    (current_price < self.data['EMA'].iloc[i] * 1.05) and
                    (self.data['MACD_12_26_9'].iloc[i] > self.data['MACDs_12_26_9'].iloc[i] * 0.8) and
                    (self.data['RSI'].iloc[i] < self.rsi_buy_threshold) and
                    (current_price > self.data['Volatility_Lower'].iloc[i])  # Price above volatility lower band
                )
            )

            # Enhanced sell condition
            sell_condition = (
                self.data['scalp_sell_signal'].iloc[i] or
                current_regime == -1 or  # Exit in bearish regime
                trend_direction == -1 or  # Exit in downtrend
                (
                    # Original condition with improvements
                    (current_price < self.data['EMA'].iloc[i] * 0.95) and
                    (current_price >= self.data['BBU_20_2.0'].iloc[i] * 0.95) and
                    (self.data['RSI'].iloc[i] < self.rsi_sell_threshold) and
                    (self.data['MACD_12_26_9'].iloc[i] < self.data['MACDs_12_26_9'].iloc[i] * 1.2) and
                    (current_price > self.data['Volatility_Upper'].iloc[i])  # Price above volatility upper band
                )
            )

            # Position management
            if not in_position and buy_condition:
                self.data.loc[self.data.index[i], 'Signal'] = 1
                self.data.loc[self.data.index[i], 'Entry_Price'] = current_price
                self.data.loc[self.data.index[i], 'Position_Size'] = position_size
                trailing_stop = current_price * (1 - self.trailing_stop_loss)
                entry_price = current_price
                max_price = current_price
                in_position = True

            elif in_position:
                # Update trailing stop
                if current_price > max_price:
                    max_price = current_price
                    trailing_stop = max_price * (1 - self.trailing_stop_loss)

                # Exit conditions
                if (sell_condition or 
                    current_price <= trailing_stop or 
                    (current_price - entry_price) / entry_price >= self.max_profit_target):
                    
                    self.data.loc[self.data.index[i], 'Signal'] = -1
                    self.data.loc[self.data.index[i], 'Exit_Price'] = current_price
                    self.data.loc[self.data.index[i], 'Trailing_Stop'] = trailing_stop
                    in_position = False
        
        # Force exit at the end of the data if still in position
        if in_position:
            last_idx = len(self.data) - 1
            self.data.loc[self.data.index[last_idx], 'Signal'] = -1
            self.data.loc[self.data.index[last_idx], 'Exit_Price'] = self.data['close'].iloc[last_idx]
            self.data.loc[self.data.index[last_idx], 'Trailing_Stop'] = trailing_stop
        
        # Count trades
        num_buys = len(self.data[self.data['Signal'] == 1])
        num_sells = len(self.data[self.data['Signal'] == -1])
        print(f"Generated {num_buys} buy signals and {num_sells} sell signals")

    def _print_performance_summary(self, performance):
        """
        Print a summary of backtest performance metrics
        """
        print("\nPerformance Summary:")
        for metric, value in performance.items():
            if isinstance(value, float):
                if metric in ['Max Drawdown', 'Win Rate', 'Average Drawdown', 'Average Profit', 'Max Profit', 'Max Loss']:
                    print(f"{metric}: {value:.2%}")
                elif metric in ['Sharpe Ratio', 'Calmar Ratio', 'Sortino Ratio', 'Profit Factor']:
                    print(f"{metric}: {value:.2f}")
                else:
                    print(f"{metric}: {value:.4f}")
            else:
                print(f"{metric}: {value}")
        print("-" * 50)

    def plot_results(self, file_name=None, show_plot=False):
        """
        Enhanced plotting with scalping-specific indicators.
        
        :param file_name: Base filename for saving plot
        :param show_plot: Whether to display the plot interactively
        """
        performance, trades, equity_curve = self.calculate_performance()

        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(16, 24), height_ratios=[2, 1, 1, 1])

        # Title with file name if provided
        title_prefix = f"Results for {file_name}: " if file_name else ""

        # Price action and signals
        ax1.plot(self.data['close'], label='Close Price', alpha=0.7)
        ax1.plot(self.data['short_ema'], label=f'Short EMA ({self.scalping_window})', linestyle='--', color='orange')
        ax1.plot(self.data['medium_ema'], label=f'Medium EMA ({self.scalping_window*2})', linestyle='--', color='purple')
        ax1.plot(self.data['BBL_20_2.0'], label='Lower BB', linestyle='--', color='green')
        ax1.plot(self.data['BBU_20_2.0'], label='Upper BB', linestyle='--', color='red')

        buy_signals = self.data[self.data['Signal'] == 1]
        sell_signals = self.data[self.data['Signal'] == -1]
        
        ax1.scatter(buy_signals.index, buy_signals['close'], color='green', marker='^', label='Buy Signal')
        ax1.scatter(sell_signals.index, sell_signals['close'], color='red', marker='v', label='Sell Signal')
        ax1.set_title(f'{title_prefix}Price Action and Signals')
        ax1.legend(loc='upper left')
        ax1.grid(True, alpha=0.3)

        # Volume analysis
        ax2.bar(self.data.index, self.data['volume'], alpha=0.3, label='Volume')
        ax2.plot(self.data.index, self.data['volume_ma'], color='red', label='Volume MA')
        ax2.set_title('Volume Analysis')
        ax2.legend(loc='upper left')
        ax2.grid(True, alpha=0.3)

        # Equity curve
        ax3.plot(self.data.index[:len(equity_curve)], equity_curve, label='Equity Curve', color='blue')
        ax3.set_title('Equity Curve')
        ax3.grid(True, alpha=0.3)
        ax3.legend(loc='upper left')

        # Correlation heatmap
        try:
            correlation_matrix = self.data[['close', 'short_ema', 'medium_ema', 'RSI', 
                                        'MACD_12_26_9', 'volume_ratio', 'momentum']].corr()
            sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='coolwarm', ax=ax4)
            ax4.set_title('Correlation Heatmap of Indicators')
        except Exception as e:
            print(f"Error generating correlation heatmap: {str(e)}")
            ax4.text(0.5, 0.5, f"Error generating heatmap: {str(e)}", 
                    horizontalalignment='center', verticalalignment='center')

        plt.tight_layout()
        
        # Save the plot if a file name is provided
        if file_name:
            plt.savefig(f"{file_name}_results.png")
            print(f"Plot saved to {file_name}_results.png")
            
        if show_plot:
            plt.show()
        else:
            plt.close(fig)

    def calculate_performance(self):
        """
        Calculate performance metrics for the backtest.
        """
        # Get the trades
        entries = self.data[self.data['Signal'] == 1]
        exits = self.data[self.data['Signal'] == -1]
        
        if len(entries) == 0 or len(exits) == 0:
            print("Warning: No trades found in the backtest")
            return {
                'Total Trades': 0,
                'Win Rate': 0,
                'Average Profit': 0,
                'Max Profit': 0,
                'Max Loss': 0,
                'Max Drawdown': 0,
                'Profit Factor': 0,
                'Sharpe Ratio': 0,
                'Calmar Ratio': 0,
                'Sortino Ratio': 0
            }, [], [1.0]
        
        # Ensure equal number of entries and exits
        min_trades = min(len(entries), len(exits))
        entries = entries.iloc[:min_trades]
        exits = exits.iloc[:min_trades]
        
        # Calculate trade-by-trade performance
        trades = []
        for i in range(min_trades):
            entry_price = entries['Entry_Price'].iloc[i]
            exit_price = exits['Exit_Price'].iloc[i]
            profit_pct = (exit_price - entry_price) / entry_price
            
            trade = {
                'Entry Date': entries.index[i],
                'Exit Date': exits.index[i],
                'Entry Price': entry_price,
                'Exit Price': exit_price,
                'Profit %': profit_pct
            }
            trades.append(trade)
        
        # Convert to DataFrame for easier analysis
        trades_df = pd.DataFrame(trades)
        
        # Calculate equity curve
        equity_curve = [1.0]  # Start with 1.0 (100%)
        for profit in trades_df['Profit %']:
            equity_curve.append(equity_curve[-1] * (1 + profit))
        
        # Calculate performance metrics
        total_trades = len(trades_df)
        winning_trades = trades_df[trades_df['Profit %'] > 0]
        losing_trades = trades_df[trades_df['Profit %'] <= 0]
        
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        
        avg_profit = trades_df['Profit %'].mean() if total_trades > 0 else 0
        max_profit = trades_df['Profit %'].max() if total_trades > 0 else 0
        max_loss = trades_df['Profit %'].min() if total_trades > 0 else 0
        
        # Calculate drawdown
        drawdowns = []
        peak = equity_curve[0]
        for value in equity_curve:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            drawdowns.append(drawdown)
        
        max_drawdown = max(drawdowns) if drawdowns else 0
        avg_drawdown = sum(drawdowns) / len(drawdowns) if drawdowns else 0
        
        # Calculate risk-adjusted returns
        daily_returns = np.diff(equity_curve) / equity_curve[:-1]
        sharpe_ratio = (np.mean(daily_returns) - self.risk_free_rate) / np.std(daily_returns) if len(daily_returns) > 0 and np.std(daily_returns) > 0 else 0
        
        # Calmar ratio (annualized return / max drawdown)
        annualized_return = (equity_curve[-1] / equity_curve[0]) ** (252 / len(equity_curve)) - 1 if len(equity_curve) > 1 else 0
        calmar_ratio = annualized_return / max_drawdown if max_drawdown > 0 else 0
        
        # Sortino ratio (annualized return / downside deviation)
        negative_returns = [r for r in daily_returns if r < 0]
        downside_deviation = np.std(negative_returns) if negative_returns else 0
        sortino_ratio = (np.mean(daily_returns) - self.risk_free_rate) / downside_deviation if downside_deviation > 0 else 0
        
        # Profit factor (gross profit / gross loss)
        gross_profit = winning_trades['Profit %'].sum() if len(winning_trades) > 0 else 0
        gross_loss = abs(losing_trades['Profit %'].sum()) if len(losing_trades) > 0 else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf') if gross_profit > 0 else 0
        
        performance = {
            'Total Trades': total_trades,
            'Win Rate': win_rate,
            'Average Profit': avg_profit,
            'Max Profit': max_profit,
            'Max Loss': max_loss,
            'Max Drawdown': max_drawdown,
            'Average Drawdown': avg_drawdown,
            'Profit Factor': profit_factor,
            'Sharpe Ratio': sharpe_ratio,
            'Calmar Ratio': calmar_ratio,
            'Sortino Ratio': sortino_ratio
        }
        
        return performance, trades, equity_curve

# Main execution code
