import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class DOM_Scalping(Strategy):
    # Strategy parameters
    order_book_monitor_bid_ask = True
    order_book_monitor_order_flow = True

    def init(self):
        # Initialize indicators

    def next(self):
        # Get current values
        price = self.data.Close[-1]
