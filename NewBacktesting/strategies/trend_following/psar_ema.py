# strategies/psar_ema.py

import pandas as pd
import numpy as np

class HybridPSAREMA:
    def __init__(self, data):
        self.data = data
        self.data['EMA'] = self.calculate_ema(5)
        self.data['PSAR'] = self.calculate_psar()
        self.data['Signal'] = self.generate_signals()

    def calculate_ema(self, period):
        """Calculate the Exponential Moving Average."""
        return self.data['Close'].ewm(span=period, adjust=False).mean()

    def calculate_psar(self):
        """Calculate the Parabolic Stop and Reverse (PSAR)."""
        # Initialize PSAR values
        self.data['PSAR'] = 0.0
        self.data['PSAR'][0] = self.data['Close'][0]  # Starting PSAR value
        self.data['EP'] = 0.0  # Extreme Point
        self.data['AF'] = 0.02  # Acceleration Factor
        self.data['Trend'] = 1  # 1 for up, -1 for down

        for i in range(1, len(self.data)):
            if self.data['Trend'][i-1] == 1:  # Uptrend
                self.data['PSAR'][i] = self.data['PSAR'][i-1] + self.data['AF'][i-1] * (self.data['EP'][i-1] - self.data['PSAR'][i-1])
                if self.data['Close'][i] < self.data['PSAR'][i]:  # Trend reversal
                    self.data['Trend'][i] = -1
                    self.data['PSAR'][i] = self.data['EP'][i-1]  # Set PSAR to previous EP
                    self.data['AF'][i] = 0.02  # Reset AF
                else:
                    self.data['Trend'][i] = 1
                    self.data['EP'][i] = max(self.data['EP'][i-1], self.data['Close'][i])  # Update EP
                    self.data['AF'][i] = min(self.data['AF'][i-1] + 0.02, 0.2)  # Increase AF
            else:  # Downtrend
                self.data['PSAR'][i] = self.data['PSAR'][i-1] + self.data['AF'][i-1] * (self.data['EP'][i-1] - self.data['PSAR'][i-1])
                if self.data['Close'][i] > self.data['PSAR'][i]:  # Trend reversal
                    self.data['Trend'][i] = 1
                    self.data['PSAR'][i] = self.data['EP'][i-1]  # Set PSAR to previous EP
                    self.data['AF'][i] = 0.02  # Reset AF
                else:
                    self.data['Trend'][i] = -1
                    self.data['EP'][i] = min(self.data['EP'][i-1], self.data['Close'][i])  # Update EP
                    self.data['AF'][i] = min(self.data['AF'][i-1] + 0.02, 0.2)  # Increase AF

        return self.data['PSAR']

    def generate_signals(self):
        """Generate buy/sell signals based on PSAR and EMA conditions."""
        signals = []
        for i in range(len(self.data)):
            if i < 2:  # Not enough data for three consecutive periods
                signals.append('HOLD')
                continue
            
            psar_up = self.data['PSAR'][i] < self.data['Close'][i]
            ema_up = self.data['Close'][i] > self.data['EMA'][i]
            psar_down = self.data['PSAR'][i] > self.data['Close'][i]
            ema_down = self.data['Close'][i] < self.data['EMA'][i]

            if psar_up and ema_up and all(psar_up and ema_up for j in range(i-2, i+1)):
                signals.append('BUY')
            elif psar_down and ema_down and all(psar_down and ema_down for j in range(i-2, i+1)):
                signals.append('SELL')
            else:
                signals.append('HOLD')
        
        return signals

# Example usage:
# data = pd.DataFrame({'Close': [...]})  # Replace with actual closing prices
# strategy = HybridPSAREMA(data)
# print(strategy.data[['Close', 'EMA', 'PSAR', 'Signal']])

