import pandas as pd
import talib
from backtesting import Strategy
from backtesting.lib import crossover

# data_path = 'C:/Users/MoonBots/Desktop/code/1_backtesting/data/hl_data'

# First, read without usecols and see the columns
# data = pd.read_csv(data_path, parse_dates=['datetime'], index_col='datetime')
# print("Columns found initially:", data.columns)

# Drop unnamed columns if any
# data = data.loc[:, ~data.columns.str.contains('^Unnamed')]
# data.columns = data.columns.str.strip().str.lower()  # make columns lowercase and strip whitespace
# print("Columns after cleaning:", data.columns)

# Now rename if they match known lowercase names
# rename_map = {'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}
# if all(col in data.columns for col in rename_map.keys()):
#     data.rename(columns=rename_map, inplace=True)
#     data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
# else:
#     raise ValueError("Required columns not found in the CSV.")

class TrixStrategy(Strategy):
    trix_period = 14
    signal_period = 9

    def init(self):
        super().init()
        self.trix = self.I(talib.TRIX, self.data.Close, self.trix_period)
        self.signal = self.I(talib.EMA, self.trix, self.signal_period)

    def next(self):
        trix_above_zero = self.trix[-1] > 0 and self.trix[-2] <= 0
        trix_below_zero = self.trix[-1] < 0 and self.trix[-2] >= 0

        trix_cross_up = crossover(self.trix, self.signal)
        trix_cross_down = crossover(self.signal, self.trix)

        if trix_above_zero and trix_cross_up and not self.position.is_long:
            self.position.close()
            self.buy()

        if trix_below_zero and trix_cross_down and not self.position.is_short:
            self.position.close()
            self.sell()
