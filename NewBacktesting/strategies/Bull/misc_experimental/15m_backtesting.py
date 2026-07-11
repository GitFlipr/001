import pandas as pd
import numpy as np
import pandas_ta as ta
import matplotlib.pyplot as plt
from scipy import stats
import os
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class Backtesting:
    def __init__(self, 
                 data_directory,
                 timeframe='15minute',
                 ema_period=20, 
                 bb_period=20, 
                 bb_std=2, 
                 rsi_period=14,
                 min_profit_target=0.03, 
                 max_profit_target=0.05, 
                 trailing_stop_loss=0.02,
                 risk_free_rate=0.02,
                 initial_capital=10000,
                 max_position_size=0.1,  # Maximum 10% of capital per trade
                 min_trade_duration=5,   # Minimum 5 candles between trades
                 price_change_threshold=0.5):  # Maximum 50% price change threshold
        """
        Enhanced Backtesting class for a multi-timeframe scalping strategy.
        
        :param data_directory: Path to the directory containing CSV files
        :param timeframe: Timeframe to analyze (e.g., '15minute', '1hour', etc.)
        :param ema_period: Period for Exponential Moving Average
        :param bb_period: Period for Bollinger Bands
        :param bb_std: Standard deviation for Bollinger Bands
        :param rsi_period: Period for RSI
        :param min_profit_target: Minimum profit target percentage
        :param max_profit_target: Maximum profit target percentage
        :param trailing_stop_loss: Trailing stop loss percentage
        :param risk_free_rate: Risk-free rate percentage
        :param initial_capital: Initial capital for backtesting
        :param max_position_size: Maximum position size as fraction of capital
        :param min_trade_duration: Minimum number of candles between trades
        :param price_change_threshold: Maximum allowed price change percentage
        """
        self.data_directory = data_directory
        self.timeframe = timeframe
        self.ema_period = ema_period
        self.bb_period = bb_period
        self.bb_std = bb_std
        self.rsi_period = rsi_period
        self.min_profit_target = min_profit_target
        self.max_profit_target = max_profit_target
        self.trailing_stop_loss = trailing_stop_loss
        self.risk_free_rate = risk_free_rate
        self.initial_capital = initial_capital
        self.max_position_size = max_position_size
        self.min_trade_duration = min_trade_duration
        self.price_change_threshold = price_change_threshold
        
        self.data = self._load_all_data()
        self._validate_data()
        self._calculate_indicators()
    
    def _validate_data(self):
        """
        Validate the data for anomalies and clean if necessary.
        """
        # Group by symbol for validation
        for symbol, group in self.data.groupby('Symbol'):
            # Check for price anomalies
            price_changes = group['Close'].pct_change().abs()
            anomalous_prices = price_changes > self.price_change_threshold
            
            if anomalous_prices.any():
                print(f"Warning: Found {anomalous_prices.sum()} anomalous price changes in {symbol}")
                # Replace anomalous prices with previous valid price
                self.data.loc[anomalous_prices, 'Close'] = self.data.loc[anomalous_prices, 'Close'].shift(1)
            
            # Check for missing values
            missing_values = group.isnull().sum()
            if missing_values.any():
                print(f"Warning: Found {missing_values.sum()} missing values in {symbol}")
                # Forward fill missing values
                self.data.loc[self.data['Symbol'] == symbol] = group.ffill()
    
    def _load_all_data(self):
        """
        Load all CSV files from the specified timeframe directory.
        """
        timeframe_dir = os.path.join(self.data_directory, self.timeframe)
        all_data = []
        
        for file in os.listdir(timeframe_dir):
            if file.endswith('.csv'):
                file_path = os.path.join(timeframe_dir, file)
                try:
                    df = pd.read_csv(file_path, parse_dates=['Date'])
                    df['Symbol'] = file.replace('.csv', '')
                    
                    # Ensure data is sorted by date
                    df = df.sort_values('Date')
                    
                    # Calculate time difference between candles
                    df['Time_Diff'] = df['Date'].diff()
                    
                    # Filter out candles with too large time gaps
                    if 'minute' in self.timeframe:
                        max_gap = timedelta(minutes=int(self.timeframe.replace('minute', '')) * 2)
                    elif 'hour' in self.timeframe:
                        max_gap = timedelta(hours=int(self.timeframe.replace('hour', '')) * 2)
                    else:
                        max_gap = timedelta(days=1)
                    
                    df = df[df['Time_Diff'] <= max_gap]
                    
                    all_data.append(df)
                except Exception as e:
                    print(f"Error loading {file}: {str(e)}")
        
        if not all_data:
            raise ValueError(f"No valid CSV files found in {timeframe_dir}")
        
        # Combine all dataframes
        combined_data = pd.concat(all_data, ignore_index=True)
        combined_data.set_index('Date', inplace=True)
        combined_data.sort_index(inplace=True)
        
        # Convert 'Close' column to numeric, forcing errors to NaN
        combined_data['Close'] = pd.to_numeric(combined_data['Close'], errors='coerce')
        
        return combined_data
    
    def _calculate_indicators(self):
        """
        Calculate enhanced technical indicators.
        """
        # Group by symbol to calculate indicators for each symbol separately
        grouped = self.data.groupby('Symbol')
        
        for symbol, group in grouped:
            # EMA
            self.data.loc[self.data['Symbol'] == symbol, 'EMA'] = group['Close'].ewm(span=self.ema_period, adjust=False).mean()
            
            # Bollinger Bands
            bb = ta.bbands(group['Close'], length=self.bb_period, std=self.bb_std)
            for col in bb.columns:
                self.data.loc[self.data['Symbol'] == symbol, col] = bb[col]
            
            # RSI
            self.data.loc[self.data['Symbol'] == symbol, 'RSI'] = ta.rsi(group['Close'], length=self.rsi_period)
            
            # MACD
            macd = ta.macd(group['Close'])
            for col in macd.columns:
                self.data.loc[self.data['Symbol'] == symbol, col] = macd[col]
            
            # Volume Weighted Average Price (VWAP)
            self.data.loc[self.data['Symbol'] == symbol, 'VWAP'] = ta.vwap(
                high=group['High'],
                low=group['Low'],
                close=group['Close'],
                volume=group['Volume']
            )
            
            # Stochastic RSI
            stoch_rsi = ta.stochrsi(group['Close'])
            for col in stoch_rsi.columns:
                self.data.loc[self.data['Symbol'] == symbol, col] = stoch_rsi[col]
            
            # Average True Range (ATR)
            atr = ta.atr(high=group['High'], low=group['Low'], close=group['Close'])
            self.data.loc[self.data['Symbol'] == symbol, 'ATR'] = atr
    
    def backtest(self):
        """
        Execute the backtest with enhanced entry/exit conditions and risk management.
        """
        self.data['Signal'] = 0  # Buy = 1, Sell = -1
        self.data['Entry_Price'] = np.nan
        self.data['Exit_Price'] = np.nan
        self.data['Trailing_Stop'] = np.nan
        self.data['Position_Size'] = np.nan
        self.data['Trade_Active'] = False
        
        in_position = False
        entry_price = 0
        max_price = 0
        trailing_stop = 0
        current_symbol = None
        last_trade_time = None
        
        for i in range(1, len(self.data)):
            current_price = self.data['Close'].iloc[i]
            current_symbol = self.data['Symbol'].iloc[i]
            current_time = self.data.index[i]
            
            # Skip if we're in a position and it's not the same symbol
            if in_position and current_symbol != self.data['Symbol'].iloc[i-1]:
                continue
            
            # Check minimum trade duration
            if last_trade_time is not None:
                time_diff = current_time - last_trade_time
                if time_diff < timedelta(minutes=self.min_trade_duration):
                    continue
            
            # Enhanced Buy condition
            buy_condition = (
                current_price < self.data['EMA'].iloc[i] and
                self.data['MACD_12_26_9'].iloc[i] > self.data['MACDs_12_26_9'].iloc[i] and
                self.data['RSI'].iloc[i] < 30 and
                self.data['STOCHRSIk_14_14_3_3'].iloc[i] < 20 and
                current_price < self.data['VWAP'].iloc[i] and
                self.data['Close'].iloc[i] > self.data['BBL_20_2.0'].iloc[i]  # Price above lower BB
            )
            
            # Enhanced Sell condition
            sell_condition = (
                self.data['Close'].iloc[i-1] >= self.data['EMA'].iloc[i-1] and 
                current_price < self.data['EMA'].iloc[i] and
                current_price >= self.data['BBU_20_2.0'].iloc[i] and
                self.data['RSI'].iloc[i] < 70 and
                self.data['MACD_12_26_9'].iloc[i] < self.data['MACDs_12_26_9'].iloc[i] and
                self.data['STOCHRSIk_14_14_3_3'].iloc[i] > 80
            )
            
            # Buy signal
            if not in_position and buy_condition:
                # Calculate position size based on ATR and risk management
                atr = self.data['ATR'].iloc[i]
                risk_amount = self.initial_capital * 0.01  # Risk 1% of capital
                position_size = min(
                    risk_amount / (atr * 2),  # Use ATR for stop loss
                    self.initial_capital * self.max_position_size / current_price
                )
                
                self.data.loc[self.data.index[i], 'Signal'] = 1
                self.data.loc[self.data.index[i], 'Entry_Price'] = current_price
                self.data.loc[self.data.index[i], 'Position_Size'] = position_size
                self.data.loc[self.data.index[i], 'Trade_Active'] = True
                
                trailing_stop = current_price * (1 - self.trailing_stop_loss)
                entry_price = current_price
                in_position = True
                last_trade_time = current_time
            
            # Manage position
            if in_position:
                # Update trailing stop
                if current_price > max_price:
                    max_price = current_price
                    trailing_stop = max_price * (1 - self.trailing_stop_loss)
                
                # Check for profit target
                profit_target = entry_price * (1 + self.min_profit_target)
                if current_price >= profit_target:
                    trailing_stop = max(trailing_stop, entry_price * (1 + self.min_profit_target * 0.5))
                
                # Exit condition
                if sell_condition or current_price <= trailing_stop:
                    self.data.loc[self.data.index[i], 'Signal'] = -1
                    self.data.loc[self.data.index[i], 'Exit_Price'] = current_price
                    self.data.loc[self.data.index[i], 'Trailing_Stop'] = trailing_stop
                    self.data.loc[self.data.index[i], 'Trade_Active'] = False
                    in_position = False
    
    def calculate_performance(self):
        """
        Calculate enhanced performance metrics for the backtest.
        """
        buy_signals = self.data[self.data['Signal'] == 1]
        sell_signals = self.data[self.data['Signal'] == -1]
        
        trades = []
        equity_curve = [self.initial_capital]  # Start with initial capital
        max_drawdown = 0
        peak = self.initial_capital
        
        # Initialize returns array
        returns_array = np.array([])
        daily_returns = []
        
        for buy_idx, buy in buy_signals.iterrows():
            sell_candidates = sell_signals[sell_signals.index > buy_idx]
            if not sell_candidates.empty:
                sell = sell_candidates.iloc[0]
                position_size = buy['Position_Size']
                trade_return = (sell['Close'] - buy['Close']) / buy['Close']
                trade_pnl = position_size * (sell['Close'] - buy['Close'])
                
                # Skip trades with unrealistic returns
                if abs(trade_return) > self.price_change_threshold:
                    continue
                
                trade = {
                    'Symbol': buy['Symbol'],
                    'Buy Date': buy_idx,
                    'Sell Date': sell.name,
                    'Buy Price': buy['Close'],
                    'Sell Price': sell['Close'],
                    'Position Size': position_size,
                    'Return': trade_return,
                    'PnL': trade_pnl
                }
                trades.append(trade)
                
                # Update equity curve
                equity_curve.append(equity_curve[-1] + trade_pnl)
                
                # Update maximum drawdown
                peak = max(peak, equity_curve[-1])
                drawdown = (peak - equity_curve[-1]) / peak
                max_drawdown = max(max_drawdown, drawdown)
        
        # Calculate daily returns for Sharpe ratio
        if len(equity_curve) > 1:
            for i in range(1, len(equity_curve)):
                daily_return = (equity_curve[i] / equity_curve[i-1]) - 1
                daily_returns.append(daily_return)
            
            returns_array = np.array(daily_returns)
        
        # Calculate metrics
        trade_returns = [t['Return'] for t in trades]
        
        # Initialize performance metrics with default values
        performance = {
            'Total Trades': len(trades),
            'Winning Trades': sum(1 for r in trade_returns if r > 0),
            'Losing Trades': sum(1 for r in trade_returns if r <= 0),
            'Win Rate': 0.0,
            'Average Return': 0.0,
            'Total Return': 0.0,
            'Max Drawdown': 0.0,
            'Sharpe Ratio': 0.0,
            'Calmar Ratio': 0.0,
            'Sortino Ratio': 0.0,
            'Average Drawdown': 0.0,
            'Final Equity': self.initial_capital,
            'Profit Factor': 0.0
        }
        
        # Update metrics if we have trades
        if trades:
            performance['Win Rate'] = sum(1 for r in trade_returns if r > 0) / len(trade_returns)
            performance['Average Return'] = np.mean(trade_returns)
            performance['Total Return'] = (equity_curve[-1] / self.initial_capital) - 1
            performance['Max Drawdown'] = max_drawdown
            performance['Final Equity'] = equity_curve[-1]
            
            # Calculate profit factor
            winning_trades = sum(t['PnL'] for t in trades if t['PnL'] > 0)
            losing_trades = abs(sum(t['PnL'] for t in trades if t['PnL'] < 0))
            performance['Profit Factor'] = winning_trades / losing_trades if losing_trades > 0 else float('inf')
            
            # Calculate risk metrics if we have returns
            if len(returns_array) > 0:
                excess_returns = returns_array - (self.risk_free_rate / 252)  # Daily risk-free rate
                
                # Sharpe Ratio
                if np.std(excess_returns) != 0:
                    performance['Sharpe Ratio'] = np.sqrt(252) * (np.mean(excess_returns) / np.std(excess_returns))
                
                # Calmar Ratio
                if max_drawdown != 0:
                    performance['Calmar Ratio'] = (np.mean(returns_array) * 252) / max_drawdown
                
                # Sortino Ratio
                downside_returns = returns_array[returns_array < 0]
                if len(downside_returns) > 0 and np.std(downside_returns) != 0:
                    performance['Sortino Ratio'] = np.sqrt(252) * (np.mean(excess_returns) / np.std(downside_returns))
        
        return performance, trades, equity_curve
    
    def plot_results(self):
        """
        Plot enhanced backtesting results with multiple subplots.
        """
        performance, trades, equity_curve = self.calculate_performance()
        
        # Create figure with subplots
        fig = plt.figure(figsize=(16, 12))
        gs = plt.GridSpec(3, 2, figure=fig)
        
        # Plot 1: Price and signals
        ax1 = fig.add_subplot(gs[0, :])
        for symbol in self.data['Symbol'].unique():
            symbol_data = self.data[self.data['Symbol'] == symbol]
            ax1.plot(symbol_data.index, symbol_data['Close'], label=f'{symbol} Price', alpha=0.7)
            
            # Plot buy/sell signals
            buy_signals = symbol_data[symbol_data['Signal'] == 1]
            sell_signals = symbol_data[symbol_data['Signal'] == -1]
            ax1.scatter(buy_signals.index, buy_signals['Close'], color='green', marker='^', label=f'{symbol} Buy')
            ax1.scatter(sell_signals.index, sell_signals['Close'], color='red', marker='v', label=f'{symbol} Sell')
        
        ax1.set_title('Price Action and Signals')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # Plot 2: Equity Curve
        ax2 = fig.add_subplot(gs[1, :])
        ax2.plot(self.data.index[:len(equity_curve)], equity_curve, label='Equity Curve', color='blue')
        ax2.set_title('Equity Curve')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Portfolio Value')
        ax2.grid(alpha=0.3)
        
        # Plot 3: RSI
        ax3 = fig.add_subplot(gs[2, 0])
        for symbol in self.data['Symbol'].unique():
            symbol_data = self.data[self.data['Symbol'] == symbol]
            ax3.plot(symbol_data.index, symbol_data['RSI'], label=f'{symbol} RSI', alpha=0.7)
        ax3.axhline(y=70, color='r', linestyle='--')
        ax3.axhline(y=30, color='g', linestyle='--')
        ax3.set_title('RSI')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('RSI')
        ax3.grid(alpha=0.3)
        
        # Plot 4: MACD
        ax4 = fig.add_subplot(gs[2, 1])
        for symbol in self.data['Symbol'].unique():
            symbol_data = self.data[self.data['Symbol'] == symbol]
            ax4.plot(symbol_data.index, symbol_data['MACD_12_26_9'], label=f'{symbol} MACD', alpha=0.7)
            ax4.plot(symbol_data.index, symbol_data['MACDs_12_26_9'], label=f'{symbol} Signal', alpha=0.7)
        ax4.set_title('MACD')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('MACD')
        ax4.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.show()
