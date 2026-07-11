import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class Recovery_Scalping(Strategy):
    # Strategy parameters

    def init(self):
        # Initialize indicators

    def next(self):
        # Get current values
        price = self.data.Close[-1]
