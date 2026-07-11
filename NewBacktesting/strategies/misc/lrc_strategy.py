import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from sklearn.linear_model import LinearRegression

class LRCStrategy(Strategy):
    length = 4
    dev_threshold = 0.09

    def init(self):
        self.price = self.data.Close
        self.lrc = self.I(self.linear_regression_curve, self.price, self.length)

    def linear_regression_curve(self, prices, length):
        # prices is a numpy-like array from backtesting.py
        lrc_vals = np.full(len(prices), np.nan)
        for i in range(length, len(prices) + 1):
            # Now just use slicing directly, no .values
            y = prices[i-length:i].reshape(-1, 1)
            X = np.arange(length).reshape(-1, 1)
            model = LinearRegression()
            model.fit(X, y)
            pred = model.predict([[length - 1]])[0, 0]
            lrc_vals[i-1] = pred
        return lrc_vals

    def next(self):
        price = self.price[-1]
        lrc_val = self.lrc[-1]
        deviation = (price - lrc_val) / lrc_val

        if len(self.lrc) > 1:
            slope = self.lrc[-1] - self.lrc[-2]
        else:
            slope = 0

        prev_close = self.price[-2] if len(self.price) > 1 else price

        long_condition = (deviation < -self.dev_threshold) and (slope > 0) and (price > prev_close)
        short_condition = (deviation > self.dev_threshold) and (slope < 0) and (price < prev_close)

        long_exit_condition = price >= lrc_val
        short_exit_condition = price <= lrc_val

        if self.position.is_long:
            if long_exit_condition:
                self.position.close()
        elif self.position.is_short:
            if short_exit_condition:
                self.position.close()
        else:
            if long_condition:
                self.buy()
            elif short_condition:
                self.sell()
