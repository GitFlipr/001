import pandas as pd
import numpy as np
import pandas_ta as ta
import matplotlib.pyplot as plt
from scipy import stats
import os

class AdvancedMultiIndicatorStrategy:
    def __init__(self, 
                 data, 
                 bb_window=20, 
                 bb_std_dev=2, 
                 roc_window=14,
                 rsi_window=14,
                 macd_fast=12,
                 macd_slow=26,
                 macd_signal=9,
                 risk_free_rate=0.02):
        """
        Advanced trading strategy using multiple technical indicators with comprehensive performance analysis
        
        :param data: Historical price data DataFrame
        :param risk_free_rate: Annual risk-free rate for Sharpe ratio calculation
        """
        self.data = data.copy()
        self.risk_free_rate = risk_free_rate
        
        # Configuration parameters
        self.config = {
            'bb_window': bb_window,
            'bb_std_dev': bb_std_dev,
            'roc_window': roc_window,
            'rsi_window': rsi_window,
            'macd_fast': macd_fast,
            'macd_slow': macd_slow,
            'macd_signal': macd_signal
        }
        
        # Calculate indicators
        self._calculate_indicators()
        
        # Initialize trading signals and performance tracking
        self.signals = pd.DataFrame(index=data.index)
        self.signals['Signal'] = 0
        self.trades = []
        self.equity_curve = [1.0]  # Start with $1

    def _calculate_indicators(self):
        """
        Calculate multiple technical indicators
        """
        c = self.config
        
        # Bollinger Bands
        bbands = ta.bbands(
            self.data['Close'], 
            length=c['bb_window'], 
            std=c['bb_std_dev']
        )
        self.data['BB_Lower'] = bbands['BBL_' + str(c['bb_window']) + '_' + str(c['bb_std_dev'])]
        self.data['BB_Middle'] = bbands['BBM_' + str(c['bb_window']) + '_' + str(c['bb_std_dev'])]
        self.data['BB_Upper'] = bbands['BBU_' + str(c['bb_window']) + '_' + str(c['bb_std_dev'])]
        
        # Rate of Change
        self.data['ROC'] = ta.roc(self.data['Close'], length=c['roc_window'])
        
        # RSI
        self.data['RSI'] = ta.rsi(self.data['Close'], length=c['rsi_window'])
        
        # MACD
        macd_result = ta.macd(
            self.data['Close'], 
            fast=c['macd_fast'], 
            slow=c['macd_slow'], 
            signal=c['macd_signal']
        )
        macd_key = f"_{c['macd_fast']}_{c['macd_slow']}_{c['macd_signal']}"
        self.data['MACD'] = macd_result[f'MACD{macd_key}']
        self.data['MACD_Signal'] = macd_result[f'MACDs{macd_key}']
        
        # ATR for volatility-based stop loss
        self.data['ATR'] = ta.atr(
            self.data['High'], 
            self.data['Low'], 
            self.data['Close'], 
            length=14
        )

    def generate_signals(self, 
                          bb_touch_sensitivity=0.01,
                          roc_threshold=0,
                          rsi_overbought=70,
                          rsi_oversold=30):
        """
        Generate trading signals based on multiple indicator conditions
        """
        for i in range(1, len(self.data)):
            # Comprehensive buy conditions
            buy_conditions = (
                self.data['Close'].iloc[i] <= (self.data['BB_Lower'].iloc[i] * (1 + bb_touch_sensitivity)) and
                self.data['ROC'].iloc[i] > roc_threshold and
                self.data['RSI'].iloc[i] < rsi_oversold and
                self.data['MACD'].iloc[i] > self.data['MACD_Signal'].iloc[i]
            )
            
            # Comprehensive sell conditions
            sell_conditions = (
                self.data['Close'].iloc[i] >= (self.data['BB_Upper'].iloc[i] * (1 - bb_touch_sensitivity)) and
                self.data['ROC'].iloc[i] < -roc_threshold and
                self.data['RSI'].iloc[i] > rsi_overbought and
                self.data['MACD'].iloc[i] < self.data['MACD_Signal'].iloc[i]
            )
            
            # Assign signals
            if buy_conditions:
                self.signals.loc[self.data.index[i], 'Signal'] = 1
            elif sell_conditions:
                self.signals.loc[self.data.index[i], 'Signal'] = -1

    def backtest(self, 
                 initial_capital=100, 
                 take_profit_pct=0.03, 
                 stop_loss_pct=0.02):
        """
        Perform comprehensive backtesting with advanced risk management
        """
        self.trades = []
        capital = initial_capital
        position = 0
        entry_price = 0
        max_drawdown = 0
        peak_capital = initial_capital
        trade_returns = []
        
        for i in range(1, len(self.data)):
            current_price = self.data['Close'].iloc[i]
            
            # No open position
            if position == 0:
                if self.signals['Signal'].iloc[i] == 1:
                    shares = capital / current_price
                    position = shares
                    entry_price = current_price
                    
                    self.trades.append({
                        'Type': 'Buy',
                        'Date': self.data.index[i],
                        'Price': current_price,
                        'Shares': shares
                    })
            
            # Open long position
            elif position > 0:
                stop_loss = entry_price * (1 - stop_loss_pct)
                take_profit = entry_price * (1 + take_profit_pct)
                
                exit_conditions = (
                    current_price <= stop_loss or 
                    current_price >= take_profit or 
                    self.signals['Signal'].iloc[i] == -1
                )
                
                if exit_conditions:
                    sale_value = position * current_price
                    trade_return = (sale_value - capital) / capital
                    trade_returns.append(trade_return)
                    capital = sale_value
                    
                    # Track maximum drawdown
                    peak_capital = max(peak_capital, capital)
                    drawdown = (peak_capital - capital) / peak_capital
                    max_drawdown = max(max_drawdown, drawdown)
                    
                    self.trades.append({
                        'Type': 'Sell',
                        'Date': self.data.index[i],
                        'Price': current_price,
                        'Shares': position
                    })
                    
                    position = 0
                    entry_price = 0
        
        # Compute performance metrics
        total_trades = len(self.trades) // 2
        profitable_trades = sum(1 for tr in trade_returns if tr > 0)
        
        # Calculate daily returns for Sharpe ratio
        total_return = np.prod([1 + r for r in trade_returns]) - 1
        
        # Sharpe Ratio calculation
        if trade_returns:
            returns_array = np.array(trade_returns)
            excess_returns = returns_array - (self.risk_free_rate / 252)
            sharpe_ratio = np.sqrt(252) * (np.mean(excess_returns) / np.std(excess_returns)) if np.std(excess_returns) != 0 else 0
        else:
            sharpe_ratio = 0
        
        performance = {
            'Initial Capital': initial_capital,
            'Final Capital': capital,
            'Total Return (%)': total_return * 100,
            'Number of Trades': total_trades,
            'Win Rate (%)': (profitable_trades / total_trades) * 100 if total_trades > 0 else 0,
            'Max Drawdown (%)': max_drawdown * 100,
            'Sharpe Ratio': sharpe_ratio,
            'Average Trade Profit (%)': total_return / total_trades * 100 if total_trades > 0 else 0
        }
        
        return performance, trade_returns
    
    def plot_performance(self):
        """
        Comprehensive performance visualization
        """
        performance, trade_returns = self.backtest()
        
        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), height_ratios=[2, 1])
        
        # First subplot: Price and signals
        ax1.plot(self.data['Close'], label='Close Price', alpha=0.7)
        ax1.plot(self.data['BB_Middle'], label='Bollinger Bands (Middle)', linestyle='--', color='orange')
        ax1.fill_between(
            self.data.index, 
            self.data['BB_Lower'], 
            self.data['BB_Upper'], 
            alpha=0.1, 
            color='grey'
        )
        
        # Buy signals
        buy_signals = self.data[self.signals['Signal'] == 1]
        ax1.scatter(buy_signals.index, buy_signals['Close'], color='green', marker='^', label='Buy Signal')
        
        # Sell signals
        sell_signals = self.data[self.signals['Signal'] == -1]
        ax1.scatter(sell_signals.index, sell_signals['Close'], color='red', marker='v', label='Sell Signal')
        
        ax1.set_title('Price Action and Trading Signals')
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # Second subplot: Cumulative returns
        cum_returns = [1]
        for tr in trade_returns:
            cum_returns.append(cum_returns[-1] * (1 + tr))
        
        ax2.plot(self.data.index[-len(cum_returns):], cum_returns, label='Cumulative Returns', color='blue')
        ax2.set_title('Cumulative Portfolio Returns')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Portfolio Value')
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.show()

def load_historical_data(file_path):
    try:
        data = pd.read_csv(file_path, parse_dates=['Date'])
        data.set_index('Date', inplace=True)
        
        required_columns = ['Open', 'High', 'Low', 'Close']
        if not all(col in data.columns for col in required_columns):
            raise ValueError("CSV data must contain Open, High, Low, and Close prices.")
        
        return data
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def run_strategy_optimization(data, start_date=None, end_date=None, initial_capital=100):
    """
    Run comprehensive parameter optimization and strategy analysis
    """
    if start_date and end_date:
        data = data.loc[start_date:end_date]
    
    if data is None or data.empty:
        print("No data available for analysis.")
        return None
    
    # Define parameter grid for comprehensive optimization
    parameter_grid = {
        'bb_window': [15, 20, 25],
        'bb_std_dev': [1.5, 2, 2.5],
        'roc_window': [10, 14, 18],
        'rsi_window': [10, 14, 18],
        'take_profit_pct': [0.02, 0.03, 0.04],
        'stop_loss_pct': [0.01, 0.015, 0.02]
    }
    
    results = []
    
    # Comprehensive parameter combination search
    for bb_window in parameter_grid['bb_window']:
        for bb_std_dev in parameter_grid['bb_std_dev']:
            for roc_window in parameter_grid['roc_window']:
                for rsi_window in parameter_grid['rsi_window']:
                    for tp_pct in parameter_grid['take_profit_pct']:
                        for sl_pct in parameter_grid['stop_loss_pct']:
                            strategy = AdvancedMultiIndicatorStrategy(
                                data, 
                                bb_window=bb_window, 
                                bb_std_dev=bb_std_dev, 
                                roc_window=roc_window,
                                rsi_window=rsi_window
                            )
                            
                            strategy.generate_signals()
                            performance, trade_returns = strategy.backtest(
                                initial_capital=initial_capital,
                                take_profit_pct=tp_pct,
                                stop_loss_pct=sl_pct
                            )
                            
                            # Aggregate performance metrics with parameters
                            result_record = {
                                **performance,
                                'BB_Window': bb_window,
                                'BB_Std_Dev': bb_std_dev,
                                'ROC_Window': roc_window,
                                'RSI_Window': rsi_window,
                                'Take_Profit_Pct': tp_pct,
                                'Stop_Loss_Pct': sl_pct
                            }
                            
                            results.append(result_record)
    
    # Convert to DataFrame and sort
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values(['Total Return (%)', 'Sharpe Ratio'], ascending=False)
    
    return results_df

def main():
    # Set the data directory
    data_dir = r'C:\Users\MoonBots\Desktop\code\Backtesting\Data\hl_data'
    print(f"Starting backtesting for files in {data_dir}")
    
    # Process all subdirectories
    for timeframe_dir in os.listdir(data_dir):
        timeframe_path = os.path.join(data_dir, timeframe_dir)
        if os.path.isdir(timeframe_path):
            print(f"\nProcessing timeframe: {timeframe_dir}")
            
            # Process all CSV files in the timeframe directory
            for filename in os.listdir(timeframe_path):
                if filename.endswith('.csv'):
                    file_path = os.path.join(timeframe_path, filename)
                    print(f"\nProcessing {filename} in {timeframe_dir}")
                    
                    data = load_historical_data(file_path)
                    if data is not None:
                        # Run strategy optimization
                        optimization_results = run_strategy_optimization(data)
                        
                        # Display top strategies
                        print(f"\nTop 10 Strategies for {filename} ({timeframe_dir}):")
                        print(optimization_results.head(10))
                        
                        # Detailed analysis of best strategy
                        best_strategy_params = optimization_results.iloc[0]
                        print("\nBest Strategy Parameters:")
                        print(best_strategy_params)
                        print("\n" + "="*50 + "\n")
