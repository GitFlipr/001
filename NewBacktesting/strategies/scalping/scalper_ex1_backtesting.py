import pandas as pd
import numpy as np
import pandas_ta as ta
import matplotlib.pyplot as plt
from scipy import stats
import os

class Backtesting:
    def __init__(self, 
                 data_file, 
                 ema_period=20, 
                 bb_period=20, 
                 bb_std=2, 
                 rsi_period=14,
                 min_profit_target=0.03, 
                 max_profit_target=0.05, 
                 trailing_stop_loss=0.02,
                 risk_free_rate=0.02):
        """
        Improved Backtesting class for a scalping strategy.
        
        :param data_file: Path to the CSV file with historical price data
        :param ema_period: Period for Exponential Moving Average
        :param bb_period: Period for Bollinger Bands
        :param bb_std: Standard deviation for Bollinger Bands
        :param rsi_period: Period for RSI
        :param min_profit_target: Minimum profit target percentage
        :param max_profit_target: Maximum profit target percentage
        :param trailing_stop_loss: Trailing stop loss percentage
        :param risk_free_rate: Risk-free rate percentage
        """
        self.data_file = data_file
        self.ema_period = ema_period
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.min_profit_target = min_profit_target
        self.max_profit_target = max_profit_target
        self.trailing_stop_loss = trailing_stop_loss
        self.risk_free_rate = risk_free_rate
        
        self.data = self._load_data()
        self._calculate_indicators()
    
    def _load_data(self):
        """
        Load historical data from a CSV file.
        """
        data = pd.read_csv(self.data_file, parse_dates=['Date'])
        data.set_index('Date', inplace=True)
        
        # Convert columns to numeric, forcing errors to NaN
        data['Close'] = pd.to_numeric(data['Close'], errors='coerce')
        
        return data
    
    def _calculate_indicators(self):
        """
        Calculate advanced technical indicators.
        """
        # EMA
        self.data['EMA'] = self.data['Close'].ewm(span=self.ema_period, adjust=False).mean()
        
        # Bollinger Bands
        bb = ta.bbands(self.data['Close'], length=self.bb_period, std=self.bb_std)
        self.data = pd.concat([self.data, bb], axis=1)
        
        # RSI
        self.data['RSI'] = ta.rsi(self.data['Close'], length=self.rsi_period)
        
        # Additional indicators for confirmation
        self.data['MACD'] = ta.macd(self.data['Close'])['MACDh_12_26_9']
        self.data['ADX'] = ta.adx(self.data['High'], self.data['Low'], self.data['Close'])['ADX_14']
        
        # Volume moving average
        self.data['Volume_MA'] = ta.sma(self.data['Volume'], length=20)
    
    def backtest(self):
        """
        Enhanced backtest with more robust entry and exit conditions.
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
            
            # Enhanced Buy Conditions
            buy_condition = (
                current_price < self.data['EMA'].iloc[i] and  # Price below EMA
                self.data['RSI'].iloc[i] < 30 and  # Oversold condition
                self.data['MACD'].iloc[i] > 0 and  # Bullish MACD
                self.data['ADX'].iloc[i] > 20 and  # Strong trend confirmation
                current_price >= self.data['BBL_20_2.0'].iloc[i] and  # Above lower Bollinger Band
                self.data['Volume'].iloc[i] > self.data['Volume_MA'].iloc[i]  # Volume confirmation
            )
            
            # Enhanced Sell Conditions
            sell_condition = (
                self.data['Close'].iloc[i-1] >= self.data['EMA'].iloc[i-1] and 
                current_price < self.data['EMA'].iloc[i] and
                current_price >= self.data['BBU_20_2.0'].iloc[i] and
                self.data['RSI'].iloc[i] > 70 and  # Overbought condition
                self.data['MACD'].iloc[i] < 0 and  # Bearish MACD
                self.data['ADX'].iloc[i] > 20 and  # Strong trend confirmation
                self.data['Volume'].iloc[i] > self.data['Volume_MA'].iloc[i]  # Volume confirmation
            )
            
            # Buy signal
            if not in_position and buy_condition:
                self.data.loc[self.data.index[i], 'Signal'] = 1
                self.data.loc[self.data.index[i], 'Entry_Price'] = current_price
                trailing_stop = current_price * (1 - self.trailing_stop_loss)
                entry_price = current_price
                max_price = current_price
                in_position = True
            
            # Manage position
            if in_position:
                # Dynamic trailing stop (more aggressive)
                if current_price > max_price:
                    max_price = current_price
                    trailing_stop = max_price * (1 - self.trailing_stop_loss * 0.5)  # Tighter stop
                
                # Exit condition with more nuanced rules
                if (sell_condition or 
                    current_price <= trailing_stop or 
                    (current_price - entry_price) / entry_price < -self.trailing_stop_loss * 2):
                    self.data.loc[self.data.index[i], 'Signal'] = -1
                    self.data.loc[self.data.index[i], 'Exit_Price'] = current_price
                    self.data.loc[self.data.index[i], 'Trailing_Stop'] = trailing_stop
                    in_position = False
    
    def calculate_performance(self):
        """
        Calculate performance metrics for the backtest.
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
                
                # Apply profit target constraints
                trade_return = max(self.min_profit_target, 
                                   min(trade_return, self.max_profit_target))
                
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
        daily_returns = []
        for i in range(1, len(equity_curve)):
            daily_return = (equity_curve[i] / equity_curve[i-1]) - 1
            daily_returns.append(daily_return)
        
        # Calculate Sharpe ratio (annualized)
        if daily_returns:
            returns_array = np.array(daily_returns)
            excess_returns = returns_array - (self.risk_free_rate / 252)  # Daily risk-free rate
            sharpe_ratio = np.sqrt(252) * (np.mean(excess_returns) / np.std(excess_returns)) if np.std(excess_returns) != 0 else 0
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
        Plot the backtesting results, including buy/sell signals and equity curve.
        """
        performance, trades, equity_curve = self.calculate_performance()
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), height_ratios=[2, 1])
        
        # Plot price and signals on first subplot
        ax1.plot(self.data['Close'], label='Close Price', alpha=0.7)
        ax1.plot(self.data['EMA'], label=f'EMA ({self.ema_period})', linestyle='--', color='orange')
        ax1.plot(self.data['BBL_20_2.0'], label='Lower Bollinger Band', linestyle='--', color='green')
        ax1.plot(self.data['BBU_20_2.0'], label='Upper Bollinger Band', linestyle='--', color='red')
        
        # Buy signals
        buy_signals = self.data[self.data['Signal'] == 1]
        ax1.scatter(buy_signals.index, buy_signals['Close'], color='green', marker='^', label='Buy Signal')
        
        # Sell signals
        sell_signals = self.data[self.data['Signal'] == -1]
        ax1.scatter(sell_signals.index, sell_signals['Close'], color='red', marker='v', label='Sell Signal')
        
        ax1.set_title('Price Action and Signals')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # Plot equity curve on second subplot
        ax2.plot(self.data.index[:len(equity_curve)], equity_curve, label='Equity Curve', color='blue')
        ax2.set_title('Equity Curve')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Portfolio Value')
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.show()
