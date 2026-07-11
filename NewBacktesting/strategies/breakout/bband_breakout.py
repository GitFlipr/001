import talib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from statsmodels.tsa.stattools import adfuller
from backtesting import Backtest, Strategy
from backtesting.lib import crossover


class ImprovedBollingerBandBreakoutShort(Strategy):
    # Default strategy parameters
    window = 21
    num_std = 2.7
    take_profit = 0.05  # 5% take profit
    stop_loss = 0.03    # 3% stop loss
    atr_window = 14     # ATR calculation window
    atr_multiplier = 1  # ATR-based stop-loss multiplier

    def init(self):
        # Initialize Bollinger Bands
        self.upper_band, self.middle_band, self.lower_band = self.I(
            talib.BBANDS, self.data.Close, self.window, self.num_std, self.num_std
        )
        # Initialize ATR
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, self.atr_window)

    def next(self):
        if len(self.data) < self.window + self.atr_window:
            return

        # Short entry condition: price crosses below the lower Bollinger Band
        if crossover(self.data.Close, self.lower_band) and not self.position:
            entry_price = self.data.Close[-1]
            stop_loss_price = entry_price + (self.atr[-1] * self.atr_multiplier)
            take_profit_price = entry_price * (1 - self.take_profit)
            self.sell(sl=stop_loss_price, tp=take_profit_price)


def backtest_strategy(data, cash=1000, commission=0.002):
    """
    Run the backtest for the strategy.
    """
    bt = Backtest(data, ImprovedBollingerBandBreakoutShort, cash=cash, commission=commission)
    results = bt.run()
    bt.plot()
    return results


def optimize_strategy(data, cash=1000, commission=0.002):
    """
    Optimize the strategy's parameters.
    """
    bt = Backtest(data, ImprovedBollingerBandBreakoutShort, cash=cash, commission=commission)
    return bt.optimize(
        window=range(10, 50, 5),
        num_std=np.arange(1.5, 3.5, 0.1).tolist(),
        take_profit=np.arange(0.01, 0.10, 0.01).tolist(),
        stop_loss=np.arange(0.01, 0.10, 0.01).tolist(),
        atr_multiplier=np.arange(0.5, 3.0, 0.5).tolist(),
        maximize='Equity Final [$]'
    )


def monte_carlo_simulation(data, cash=1000, commission=0.002, num_simulations=10):
    """
    Run Monte Carlo simulations to assess the robustness of the strategy.
    """
    results = []
    for _ in range(num_simulations):
        bt = Backtest(data, ImprovedBollingerBandBreakoutShort, cash=cash, commission=commission)
        equity = bt.run()._equity_curve['Equity'][-1]
        results.append(equity)
    
    results_df = pd.DataFrame(results, columns=['Equity'])
    plt.hist(results, bins=50, alpha=0.75, color='blue', edgecolor='black')
    plt.title('Monte Carlo Simulation: Final Equity Distribution')
    plt.xlabel('Equity')
    plt.ylabel('Frequency')
    plt.show()
    return results_df


def alpha_decay_analysis(data):
    """
    Perform alpha decay analysis using the Augmented Dickey-Fuller (ADF) test.
    """
    bt = Backtest(data, ImprovedBollingerBandBreakoutShort, cash=1000, commission=0.002)
    equity_curve = bt.run()._equity_curve['Equity']
    adf_result = adfuller(equity_curve)

    print("Alpha Decay Analysis:")
    print(f"ADF Statistic: {adf_result[0]}")
    print(f"p-value: {adf_result[1]}")
    if adf_result[1] < 0.05:
        print("The equity curve is stationary, indicating no significant alpha decay.")
    else:
        print("The equity curve is non-stationary, indicating potential alpha decay.")


def load_data(filepath):
    """
    Load and preprocess data for the strategy.
    
    If filepath is a directory, all CSV files in the directory will be loaded
    and concatenated into a single DataFrame.
    """
    # Check if path is a directory
    if os.path.isdir(filepath):
        print(f"Loading all CSV files from directory: {filepath}")
        all_data = []
        
        # Get all CSV files in the directory
        files = [f for f in os.listdir(filepath) if f.endswith('.csv')]
        
        if not files:
            raise FileNotFoundError(f"No CSV files found in directory: {filepath}")
            
        print(f"Found {len(files)} CSV files: {', '.join(files)}")
        
        # Load each CSV file
        for file in files:
            file_path = os.path.join(filepath, file)
            print(f"Loading: {file}")
            
            try:
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
                
                all_data.append(df)
                print(f"  Added {len(df)} rows from {file}")
                
            except Exception as e:
                print(f"  Error loading {file}: {str(e)}")
        
        if not all_data:
            raise ValueError("No valid data could be loaded from any CSV file")
            
        # Combine all DataFrames
        data = pd.concat(all_data)
        
        # Sort by date
        data = data.sort_index()
        
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
    
    # Verify required columns exist
    required_cols = {'Open', 'High', 'Low', 'Close', 'Volume'}
    if not required_cols.issubset(data.columns):
        raise ValueError(f"Data must contain the following columns: {required_cols}")
    
    print(f"Data loaded successfully. Shape: {data.shape}, Date range: {data.index.min()} to {data.index.max()}")
    return data
