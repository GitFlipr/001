import pandas as pd
import os
from backtesting import Backtest, Strategy
from backtesting.lib import resample_apply, crossover

class SilverBulletAMSessionStrategy(Strategy):
    def init(self):
        # Initialize variables to track hourly highs and lows
        self.current_hour = None
        self.hourly_high = None
        self.hourly_low = None
        self.prev_hourly_high = None
        self.prev_hourly_low = None
        self.trade_count = 0  # Counter for unique trade IDs
        self.in_session = False
        
        # Add trend indicators
        self.sma20 = self.I(lambda x: pd.Series(x).rolling(20).mean(), self.data.Close)
        self.sma50 = self.I(lambda x: pd.Series(x).rolling(50).mean(), self.data.Close)
        
        # Add momentum indicators
        def calculate_rsi(prices):
            prices = pd.Series(prices)
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        self.rsi = self.I(calculate_rsi, self.data.Close)
        
    def next(self):
        # Set the session window for the AM Session (10:00 AM to 11:00 AM)
        current_time = self.data.index[-1]
        start_time = current_time.replace(hour=10, minute=0, second=0, microsecond=0)
        end_time = current_time.replace(hour=11, minute=0, second=0, microsecond=0)

        # Update hourly high/low if we're in a new hour
        if self.current_hour != current_time.hour:
            # Store previous hour's values
            self.prev_hourly_high = self.hourly_high
            self.prev_hourly_low = self.hourly_low
            # Update current hour's values
            self.current_hour = current_time.hour
            self.hourly_high = self.data.High[-1]
            self.hourly_low = self.data.Low[-1]
        else:
            # Update high/low for current hour
            self.hourly_high = max(self.hourly_high, self.data.High[-1])
            self.hourly_low = min(self.hourly_low, self.data.Low[-1])

        # Check if we're in the trading session
        self.in_session = start_time <= current_time <= end_time

        if self.in_session and self.prev_hourly_high is not None:
            # Calculate ATR-like value (using 14-period range)
            atr = (self.data.High[-14:].max() - self.data.Low[-14:].min()) / 14 if len(self.data.Close) >= 14 else 1.0

            # Determine trend direction
            is_uptrend = self.sma20[-1] > self.sma50[-1]
            is_downtrend = self.sma20[-1] < self.sma50[-1]

            # Check momentum conditions
            rsi_oversold = self.rsi[-1] < 40  # More lenient
            rsi_overbought = self.rsi[-1] > 60  # More lenient

            # Calculate price levels for entry
            price_above_low = self.data.Close[-1] > self.prev_hourly_low
            price_below_high = self.data.Close[-1] < self.prev_hourly_high
            price_near_sma20 = abs(self.data.Close[-1] - self.sma20[-1]) / self.sma20[-1] < 0.01  # Within 1% of SMA20

            # Calculate recent price action
            recent_high = max(self.data.High[-5:])  # Last 5 candles
            recent_low = min(self.data.Low[-5:])    # Last 5 candles
            price_range = recent_high - recent_low
            price_in_range = (self.data.Close[-1] - recent_low) / price_range if price_range > 0 else 0

            # Calculate volatility and trend strength
            volatility = (self.data.High[-5:].max() - self.data.Low[-5:].min()) / self.data.Close[-5:].mean()
            trend_strength = abs(self.sma20[-1] - self.sma50[-1]) / self.sma50[-1]

            # Apply the trade execution conditions for a long position
            if (not self.position and 
                is_uptrend and  # Only trade with the trend
                price_above_low and  # Price above previous low
                price_near_sma20 and  # Price near SMA20
                rsi_oversold and  # Oversold condition
                price_in_range < 0.4 and  # Price in lower 40% of recent range
                volatility > 0.01 and  # Minimum volatility
                trend_strength > 0.001):  # Minimum trend strength
                # Calculate dynamic stop loss and take profit
                sl_distance = max(1.75 * atr, price_range * 0.35)  # Balanced stop loss
                tp_distance = sl_distance * 2.5  # 2.5:1 reward:risk ratio
                # Enter long position
                self.buy(sl=self.data.Close[-1] - sl_distance, tp=self.data.Close[-1] + tp_distance)
                self.trade_count += 1

            # Apply the trade execution conditions for a short position
            elif (not self.position and 
                  is_downtrend and  # Only trade with the trend
                  price_below_high and  # Price below previous high
                  price_near_sma20 and  # Price near SMA20
                  rsi_overbought and  # Overbought condition
                  price_in_range > 0.6 and  # Price in upper 40% of recent range
                  volatility > 0.01 and  # Minimum volatility
                  trend_strength > 0.001):  # Minimum trend strength
                # Calculate dynamic stop loss and take profit
                sl_distance = max(1.75 * atr, price_range * 0.35)  # Balanced stop loss
                tp_distance = sl_distance * 2.5  # 2.5:1 reward:risk ratio
                # Enter short position
                self.sell(sl=self.data.Close[-1] + sl_distance, tp=self.data.Close[-1] - tp_distance)
                self.trade_count += 1

        # Close all positions at the end of the session
        elif not self.in_session and self.position:
            self.position.close()
            print("Closing position at end of session")

# Load all CSV files from the directory
data_dir = 'C:/Users/MoonBots/Desktop/code/Backtesting/Data/hl_data'
all_data = []

for file in os.listdir(data_dir):
    if file.endswith('.csv'):
        file_path = os.path.join(data_dir, file)
        try:
            df = pd.read_csv(file_path, index_col=0, parse_dates=True)
            # Ensure required columns exist
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if all(col in df.columns for col in required_columns):
                all_data.append(df)
                print(f"Successfully loaded {file}")
            else:
                print(f"Skipping {file} - missing required columns")
        except Exception as e:
            print(f"Error loading {file}: {str(e)}")

if not all_data:
    print("No valid data files found. Exiting.")
    exit(1)

# Combine all data
data = pd.concat(all_data).sort_index()

# Create the Backtest instance
bt = Backtest(data, SilverBulletAMSessionStrategy,
              cash=10000, commission=.0)

# Run the backtest
output = bt.run()

# Print the backtest output
print(output)

# Plot the equity curve with resampling to avoid the plotting error
bt.plot(resample='30T')
