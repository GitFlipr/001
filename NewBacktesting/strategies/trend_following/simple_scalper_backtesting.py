# Import required libraries
import backtesting
import talib
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os
import glob

# Set up logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class ScalpingTradingStrategy(backtesting.Strategy):
    # Initialize parameters
    rsi_period = 14
    rsi_oversold = 40
    rsi_overbought = 70
    atr_period = 14
    risk_per_trade = 0.02
    reward_risk_ratio = 2.0
    atr_multiplier = 1.0
    sma_short = 10
    sma_long = 20
    
    def init(self):
        # Technical indicators
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.sma_short = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_short)
        self.sma_long = self.I(talib.SMA, self.data.Close, timeperiod=self.sma_long)
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=20)
        self.macd, self.macd_signal, self.macd_hist = self.I(talib.MACD, self.data.Close, fastperiod=12, slowperiod=26, signalperiod=9)
        self.ema_short = self.I(talib.EMA, self.data.Close, timeperiod=5)
        self.ema_long = self.I(talib.EMA, self.data.Close, timeperiod=20)

    def next(self):
        # Skip if not enough data
        if len(self.data.Close) < 20:
            return
            
        if self.position:
            current_price = self.data.Close[-1]
            entry_price = self.position.pl
            pl_pct = (current_price - (current_price - entry_price)) / (current_price - entry_price) * 100
            
            # Dynamic exit conditions
            rsi_overbought = self.rsi[-1] > self.rsi_overbought
            macd_cross_down = self.macd[-1] < self.macd_signal[-1] and self.macd[-2] > self.macd_signal[-2]
            ema_cross_down = self.ema_short[-1] < self.ema_long[-1] and self.ema_short[-2] > self.ema_long[-2]
            
            # Exit if any condition is met
            if (pl_pct <= -1 or  # Stop loss
                pl_pct >= 3 or   # Take profit
                rsi_overbought or  # RSI overbought
                macd_cross_down or  # MACD bearish crossover
                ema_cross_down):  # EMA bearish crossover
                
                self.position.close()
                logging.warning(f"Position closed at {current_price:.2f} (P/L: {pl_pct:.2f}%)")
        
        else:
            price = self.data.Close[-1]
            
            # Entry conditions - more lenient
            volume_ok = self.data.Volume[-1] >= self.volume_sma[-1] * 0.1
            trend_up = price > self.sma_short[-1] * 0.95
            rsi_oversold = self.rsi[-1] < self.rsi_oversold
            rsi_rising = self.rsi[-1] > self.rsi[-2]
            price_rising = price > self.data.Close[-2]
            macd_cross_up = self.macd[-1] > self.macd_signal[-1] and self.macd[-2] < self.macd_signal[-2]
            ema_cross_up = self.ema_short[-1] > self.ema_long[-1] and self.ema_short[-2] < self.ema_long[-2]
            
            # Log entry conditions for debugging
            if rsi_oversold:
                logging.warning(f"""
                Entry conditions:
                Price: {price:.2f}
                SMA10: {self.sma_short[-1]:.2f}
                SMA20: {self.sma_long[-1]:.2f}
                EMA5: {self.ema_short[-1]:.2f}
                EMA20: {self.ema_long[-1]:.2f}
                RSI: {self.rsi[-1]:.2f}
                Volume: {self.data.Volume[-1]:.2f}
                Volume SMA: {self.volume_sma[-1]:.2f}
                Volume OK: {volume_ok}
                Trend Up: {trend_up}
                RSI Rising: {rsi_rising}
                Price Rising: {price_rising}
                MACD Cross Up: {macd_cross_up}
                EMA Cross Up: {ema_cross_up}
                All Conditions Met: {trend_up and rsi_oversold and (rsi_rising or price_rising or macd_cross_up or ema_cross_up) and volume_ok}
                """)
            
            if (trend_up and rsi_oversold and 
                (rsi_rising or price_rising or macd_cross_up or ema_cross_up) and
                volume_ok):
                
                # Calculate position size based on ATR
                risk_amount = self.equity * self.risk_per_trade
                atr_value = self.atr[-1]
                risk_per_share = atr_value * self.atr_multiplier
                position_size = max(1, int(risk_amount / risk_per_share))
                
                # Limit position size
                max_size = int(self.equity * 0.2 / price)
                position_size = min(position_size, max_size)
                
                if position_size < 1:
                    logging.warning("Position size too small, skipping trade")
                    return
                
                # Enter the position
                self.buy(size=position_size)
                
                logging.warning(f"""
                Position opened:
                Price: {price:.2f}
                Size: {position_size} units
                Total Value: {price * position_size:.2f}
                Equity: {self.equity:.2f}
                Risk Amount: {risk_amount:.2f}
                Risk Per Share: {risk_per_share:.2f}
                RSI: {self.rsi[-1]:.2f}
                ATR: {atr_value:.2f}
                """)

# Get all CSV files from the 1hour directory
data_dir = r'C:\Users\MoonBots\Desktop\code\Backtesting\Data\hl_data\30minute'
csv_files = glob.glob(os.path.join(data_dir, '*.csv'))

# Create a DataFrame to store all results
results_df = pd.DataFrame(columns=[
    'Symbol', 'Final Equity', 'Return %', 'Max Drawdown %', 'Win Rate %',
    'Total Trades', 'Best Trade %', 'Worst Trade %', 'Avg Trade %',
    'Profit Factor', 'Sharpe Ratio', 'Sortino Ratio', 'Exposure Time %'
])

results = []
for file_path in csv_files:
    print(f"\nProcessing file: {os.path.basename(file_path)}")
    data = pd.read_csv(file_path)
    print("Original columns:", data.columns.tolist())

    # Validate and clean data
    def prepare_data(df):
        # Capitalize column names
        df.columns = [column.capitalize() for column in df.columns]
        
        # Ensure required columns exist
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Convert price columns to numeric
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Handle date column
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
            df.set_index('Date', inplace=True)
        else:
            df.index = pd.date_range(start='2020-01-01', periods=len(df), freq='1min')
            logging.warning("No Date column found. Created artificial datetime index.")
        
        # Drop Adj Close column if it exists
        if 'Adj Close' in df.columns or 'Adj close' in df.columns:
            df = df.drop(['Adj Close'] if 'Adj Close' in df.columns else ['Adj close'], axis=1)
        
        # Remove rows with missing data
        df = df.dropna()
        
        # Validate price data
        if (df['Low'] > df['High']).any():
            raise ValueError("Found Low prices greater than High prices")
        if ((df['Close'] > df['High']) | (df['Close'] < df['Low'])).any():
            raise ValueError("Found Close prices outside High-Low range")
        
        logging.info(f"Data shape after preparation: {df.shape}")
        logging.info(f"Columns in prepared data: {df.columns.tolist()}")
        
        return df

    try:
        data = prepare_data(data)
        logging.info("Data preparation completed successfully")
    except Exception as e:
        logging.error(f"Error preparing data: {str(e)}")
        raise

    # Calculate minimum volume threshold
    min_volume = data['Volume'].quantile(0.25)

    # Initialize and run backtest
    bt = backtesting.Backtest(
        data, 
        ScalpingTradingStrategy, 
        cash=100000, 
        commission=0.002
    )

    # Optimize with minimal parameters
    result = bt.optimize(
        maximize='Equity Final [$]',
        rsi_oversold=range(20, 41, 5),
        risk_per_trade=[0.02, 0.03],
        constraint=lambda param: True
    )

    # Extract symbol from filename
    symbol = os.path.basename(file_path).split('_')[0]
    
    # Store results in DataFrame
    results_df = pd.concat([results_df, pd.DataFrame({
        'Symbol': [symbol],
        'Final Equity': [result._equity_curve['Equity'].iloc[-1]],
        'Return %': [(result._equity_curve['Equity'].iloc[-1] / 100000 - 1) * 100],
        'Max Drawdown %': [result._equity_curve['DrawdownPct'].min() * 100],
        'Win Rate %': [result._trades['ReturnPct'].gt(0).mean() * 100 if not result._trades.empty else 0],
        'Total Trades': [len(result._trades)],
        'Best Trade %': [result._trades['ReturnPct'].max() if not result._trades.empty else 0],
        'Worst Trade %': [result._trades['ReturnPct'].min() if not result._trades.empty else 0],
        'Avg Trade %': [result._trades['ReturnPct'].mean() if not result._trades.empty else 0],
        'Profit Factor': [result._trades['ReturnPct'].gt(0).sum() / abs(result._trades['ReturnPct'].lt(0).sum()) if not result._trades.empty else 0],
        'Sharpe Ratio': [result._equity_curve['Equity'].pct_change().mean() / result._equity_curve['Equity'].pct_change().std() * np.sqrt(252) if len(result._equity_curve) > 1 else 0],
        'Sortino Ratio': [result._equity_curve['Equity'].pct_change().mean() / result._equity_curve['Equity'].pct_change()[result._equity_curve['Equity'].pct_change() < 0].std() * np.sqrt(252) if len(result._equity_curve) > 1 else 0],
        'Exposure Time %': [result._equity_curve['Equity'].gt(100000).mean() * 100]
    })], ignore_index=True)

    # Store results with filename
    results.append({
        'filename': os.path.basename(file_path),
        'result': result
    })

# Save results to CSV
results_df.to_csv('backtest_results.csv', index=False)

# Print summary statistics
print("\n=== Backtest Summary Statistics ===")
print(f"Total Assets Tested: {len(results_df)}")
print(f"Average Return: {results_df['Return %'].mean():.2f}%")
print(f"Median Return: {results_df['Return %'].median():.2f}%")
print(f"Best Return: {results_df['Return %'].max():.2f}% ({results_df.loc[results_df['Return %'].idxmax(), 'Symbol']})")
print(f"Worst Return: {results_df['Return %'].min():.2f}% ({results_df.loc[results_df['Return %'].idxmin(), 'Symbol']})")
print(f"Average Win Rate: {results_df['Win Rate %'].mean():.2f}%")
print(f"Average Trades per Asset: {results_df['Total Trades'].mean():.1f}")
print(f"Average Exposure Time: {results_df['Exposure Time %'].mean():.2f}%")

# Print top 5 performing assets
print("\n=== Top 5 Performing Assets ===")
print(results_df.nlargest(5, 'Return %')[['Symbol', 'Return %', 'Win Rate %', 'Total Trades']].to_string(index=False))

# Print bottom 5 performing assets
print("\n=== Bottom 5 Performing Assets ===")
print(results_df.nsmallest(5, 'Return %')[['Symbol', 'Return %', 'Win Rate %', 'Total Trades']].to_string(index=False))

# Print correlation analysis
print("\n=== Correlation Analysis ===")
correlation_matrix = results_df[['Return %', 'Win Rate %', 'Total Trades', 'Exposure Time %']].corr()
print(correlation_matrix.to_string())