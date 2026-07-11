import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class Scalper_Example_1(Strategy):
    # Strategy parameters

    def init(self):
        # Initialize indicators
        # Bollinger Bands
        def bollinger_bands(close, window, num_std):
            ma = pd.Series(close).rolling(window=window).mean()
            std = pd.Series(close).rolling(window=window).std()
            upper = ma + (std * num_std)
            lower = ma - (std * num_std)
            return upper, ma, lower

        self.upper_band, self.middle_band, self.lower_band = self.I(
            bollinger_bands, 
            self.data.Close, 
            20, 
            2.0
        )

    def next(self):
        # Get current values
        price = self.data.Close[-1]
