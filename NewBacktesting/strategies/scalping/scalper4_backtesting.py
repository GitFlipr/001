import pandas as pd
import numpy as np
import pandas_ta as ta
import matplotlib.pyplot as plt
from scipy import stats
import os

class ScalpingStrategy:
    def __init__(self, 
                 data_file, 
                 ema_period=20, 
                 kc_period=20, 
                 kc_multiplier=2, 
                 rsi_period=14,
                 stoch_period=14,
                 min_profit_target=0.03, 
                 max_profit_target=0.05, 
                 trailing_stop_loss=0.02,
                 risk_free_rate=0.02):
        """
        Advanced Scalping Strategy Backtesting Class
        
        Combines multiple technical indicators for more robust trading signals:
        - Exponential Moving Average (EMA)
        - Keltner Channels
        - Relative Strength Index (RSI)
        - Stochastic Oscillator
        """
        self.data_file = data_file
        self.ema_period = ema_period
        self.kc_period = kc_period
        self.kc_multiplier = kc_multiplier
        self.rsi_period = rsi_period
        self.stoch_period = stoch_period
        self.min_profit_target = min_profit_target
        self.max_profit_target = max_profit_target
        self.trailing_stop_loss = trailing_stop_loss
        self.risk_free_rate = risk_free_rate
        
        self.data = self._load_data()
        self._calculate_indicators()
    
    def _load_data(self):
        """
        Load and preprocess historical data from a CSV file.
        """
        data = pd.read_csv(self.data_file, parse_dates=['Date'])
        data.set_index('Date', inplace=True)
        
        # Convert 'Close' column to numeric, handling potential errors
        data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
        
        return data
    
    def _calculate_indicators(self):
        """
        Calculate comprehensive set of technical indicators:
        - EMA
        - Keltner Channels
        - RSI
        - Stochastic Oscillator
        """
        # EMA
        self.data['EMA'] = self.data['Close'].ewm(span=self.ema_period, adjust=False).mean()
        
        # Keltner Channels
        kc = ta.kc(
            high=self.data['High'], 
            low=self.data['Low'], 
            close=self.data['Close'], 
            length=self.kc_period, 
            scalar=self.kc_multiplier
        )
        self.data = pd.concat([self.data, kc], axis=1)
        
        # RSI
        self.data['RSI'] = ta.rsi(self.data['Close'], length=self.rsi_period)
        
        # Stochastic Oscillator
        stoch = ta.stoch(
            high=self.data['High'], 
            low=self.data['Low'], 
            close=self.data['Close'], 
            k=self.stoch_period
        )
        self.data = pd.concat([self.data, stoch], axis=1)
        
        # Add MACD for additional momentum confirmation
        macd = ta.macd(self.data['Close'])
        self.data = pd.concat([self.data, macd], axis=1)
    
    def backtest(self):
        """
        Execute the backtest with enhanced trading signals.
        Incorporates multiple indicators for entry and exit conditions.
        """
        self.data['Signal'] = 0  # Buy = 1, Sell = -1
        self.data['Entry_Price'] = np.nan
        self.data['Exit_Price'] = np.nan
        self.data['Trailing_Stop'] = np.nan
        
        in_position = False
        entry_price = 0
        max_price = 0
        trailing_stop = 0
        
        for i in range(1, len(self.data)):
            current_price = self.data['Close'].iloc[i]
            
            # Comprehensive Buy Condition
            buy_condition = (
                current_price < self.data['EMA'].iloc[i] and
                current_price < self.data['KC.lower'].iloc[i] and
                self.data['STOCHK'].iloc[i] > 20 and  # Stochastic not oversold
                self.data['STOCHK'].iloc[i] > self.data['STOCHD'].iloc[i] and  # Stochastic bullish crossover
                self.data['RSI'].iloc[i] > 30 and  # RSI confirmation
                self.data['MACD'].iloc[i] > self.data['MACDs'].iloc[i]  # MACD bullish
            )
            
            # Comprehensive Sell Condition
            sell_condition = (
                current_price >= self.data['EMA'].iloc[i-1] and 
                current_price < self.data['EMA'].iloc[i] and
                self.data['STOCHK'].iloc[i] < 80 and  # Stochastic not overbought
                self.data['STOCHK'].iloc[i] < self.data['STOCHD'].iloc[i] and  # Stochastic bearish crossover
                self.data['RSI'].iloc[i] < 70 and  # RSI confirmation
                self.data['MACD'].iloc[i] < self.data['MACDs'].iloc[i]  # MACD bearish
            )
            
            # Buy signal
            if not in_position and buy_condition:
                self.data.loc[self.data.index[i], 'Signal'] = 1
                self.data.loc[self.data.index[i], 'Entry_Price'] = current_price
                trailing_stop = current_price * (1 - self.trailing_stop_loss)
                entry_price = current_price
                in_position = True
                max_price = current_price
            
            # Manage position
            if in_position:
                # Update trailing stop
                if current_price > max_price:
                    max_price = current_price
                    trailing_stop = max_price * (1 - self.trailing_stop_loss)
                
                # Exit condition
                if sell_condition or current_price <= trailing_stop:
                    self.data.loc[self.data.index[i], 'Signal'] = -1
                    self.data.loc[self.data.index[i], 'Exit_Price'] = current_price
                    self.data.loc[self.data.index[i], 'Trailing_Stop'] = trailing_stop
                    in_position = False
    
    def calculate_performance(self):
        """
        Calculate comprehensive performance metrics.
        Follows the detailed approach from the original backtesting script.
        """
        buy_signals = self.data[self.data['Signal'] == 1]
        sell_signals = self.data[self.data['Signal'] == -1]
        
        trades = []
        equity_curve = [1.0]  # Start with $1
        max_drawdown = 0
        peak = 1.0
        
        for buy_idx, buy in buy_signals.iterrows():
            sell_candidates = sell_signals[sell_signals.index > buy_idx]
            if not sell_candidates.empty:
                sell = sell_candidates.iloc[0]
                trade_return = (sell['Close'] - buy['Close']) / buy['Close']
                
                trade = {
                    'Buy Date': buy_idx,
                    'Sell Date': sell.name,
                    'Buy Price': buy['Close'],
                    'Sell Price': sell['Close'],
                    'Return': trade_return
                }
                trades.append(trade)
                
                # Update equity curve
                equity_curve.append(equity_curve[-1] * (1 + trade_return))
                
                # Update maximum drawdown
                peak = max(peak, equity_curve[-1])
                drawdown = (peak - equity_curve[-1]) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate daily returns for Sharpe ratio
        daily_returns = [
            (equity_curve[i] / equity_curve[i-1]) - 1 
            for i in range(1, len(equity_curve))
        ]
        
        # Calculate Sharpe ratio (annualized)
        if daily_returns:
            returns_array = np.array(daily_returns)
            excess_returns = returns_array - (self.risk_free_rate / 252)  # Daily risk-free rate
            sharpe_ratio = np.sqrt(252) * (
                np.mean(excess_returns) / np.std(excess_returns)
            ) if np.std(excess_returns) != 0 else 0
        else:
            sharpe_ratio = 0
        
        # Calculate metrics
        trade_returns = [t['Return'] for t in trades]
        performance = {
            'Total Trades': len(trades),
            'Winning Trades': sum(1 for r in trade_returns if r > 0),
            'Losing Trades': sum(1 for r in trade_returns if r <= 0),
            'Win Rate': sum(1 for r in trade_returns if r > 0) / len(trade_returns) if trade_returns else 0,
            'Average Return': np.mean(trade_returns) if trade_returns else 0,
            'Total Return': np.prod([1 + r for r in trade_returns]) - 1 if trade_returns else 0,
            'Max Drawdown': max_drawdown,
            'Sharpe Ratio': sharpe_ratio
        }
        
        return performance, trades, equity_curve
    
    def plot_results(self):
        """
        Visualize backtesting results with enhanced plot.
        """
        performance, trades, equity_curve = self.calculate_performance()
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), height_ratios=[2, 1])
        
        # Plot price and signals on first subplot
        ax1.plot(self.data['Close'], label='Close Price', alpha=0.7)
        ax1.plot(self.data['EMA'], label=f'EMA ({self.ema_period})', linestyle='--', color='orange')
        ax1.plot(self.data['KC.lower'], label='Keltner Lower Channel', linestyle='--', color='green')
        ax1.plot(self.data['KC.upper'], label='Keltner Upper Channel', linestyle='--', color='red')
        
        # Buy signals
        buy_signals = self.data[self.data['Signal'] == 1]
        ax1.scatter(buy_signals.index, buy_signals['Close'], color='green', marker='^', label='Buy Signal')
        
        # Sell signals
        sell_signals = self.data[self.data['Signal'] == -1]
        ax1.scatter(sell_signals.index, sell_signals['Close'], color='red', marker='v', label='Sell Signal')
        
        ax1.set_title('Price Action and Trading Signals')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # Plot equity curve on second subplot
        ax2.plot(self.data.index[:len(equity_curve)], equity_curve, label='Equity Curve', color='blue')
        ax2.set_title('Portfolio Equity Curve')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Portfolio Value')
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.show()
