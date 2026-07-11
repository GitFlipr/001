from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import pandas as pd
from talib import SMA, RSI
import os

class MovingAverageRSIStrategy(Strategy):
    short_sma_period = 50
    long_sma_period = 200
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30

    def init(self):
        self.short_sma = self.I(SMA, self.data.Close, self.short_sma_period)
        self.long_sma = self.I(SMA, self.data.Close, self.long_sma_period)
        self.rsi = self.I(RSI, self.data.Close, self.rsi_period)

    def next(self):
        # Buy Entry:
        if (crossover(self.short_sma, self.long_sma) and
                self.rsi[-1] > 50 and self.rsi[-1] < self.rsi_overbought):
            self.buy()

        # Sell/Short Entry:
        elif (crossover(self.long_sma, self.short_sma) and
              self.rsi[-1] < 50 and self.rsi[-1] > self.rsi_oversold):
            self.sell()
            
        # Sell/Close Long Position:
        for trade in self.trades:
            if trade.is_long:
                if (crossover(self.long_sma, self.short_sma) or
                        self.rsi[-1] > self.rsi_overbought):
                    trade.close()
                    
        # Buy-to-Cover/Close Short Position:
        for trade in self.trades:
            if trade.is_short:
                if (crossover(self.short_sma, self.long_sma) or
                        self.rsi[-1] < self.rsi_oversold):
                    trade.close()

# Set the data directory
data_dir = r'C:\Users\MoonBots\Desktop\code\Backtesting\Data\hl_data\15minute'
print(f"Starting backtesting for files in {data_dir}")

# Process all files in the directory
for filename in os.listdir(data_dir):
    if filename.endswith('.csv'):  # Assuming the files are CSV format
        file_path = os.path.join(data_dir, filename)
        print(f"Processing {filename}")
        
        # Load the data
        historical_data = pd.read_csv(file_path)
        historical_data['Date'] = pd.to_datetime(historical_data['Date'])
        historical_data.set_index('Date', inplace=True)
        
        # Backtest configuration
        bt = Backtest(historical_data, MovingAverageRSIStrategy, cash=1000000, commission=.002)
        
        # Run backtest
        output = bt.run()
        print(f"\nResults for {filename}:")
        print(output)
        print("\n" + "="*50 + "\n")
