import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Type
from backtesting import Backtest
from vengeance_trend_strategy import VengeanceTrendStrategy

class VengeanceBacktester:
    """
    A comprehensive backtesting framework for the VengeanceTrend strategy.
    Features:
    - Parameter optimization
    - Monte Carlo simulation
    - Performance visualization
    - Risk analysis
    """
    
    def __init__(self, 
                 data_path: str,
                 strategy_class: Type[VengeanceTrendStrategy] = VengeanceTrendStrategy,
                 initial_capital: float = 1_000_000,
                 commission: float = 0.002):
        """
        Initialize the backtester.
        
        Args:
            data_path: Path to the price data CSV file
            strategy_class: Strategy class to backtest
            initial_capital: Initial capital for backtesting
            commission: Commission per trade
        """
        self.strategy_class = strategy_class
        self.data_path = data_path
        self.initial_capital = initial_capital
        self.commission = commission
        
        # Load and prepare data
        self.data = self._load_data()
        
        # Initialize backtest
        self.backtest = Backtest(
            self.data,
            self.strategy_class,
            cash=self.initial_capital,
            commission=self.commission
        )
    
    def _load_data(self) -> pd.DataFrame:
        """Load and prepare price data"""
        try:
            data = pd.read_csv(self.data_path)
            
            # Clean column names
            data.columns = data.columns.str.strip().str.lower()
            data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
            
            # Map columns to required format
            data = data.rename(columns={
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            })
            
            # Ensure datetime format
            data['datetime'] = pd.to_datetime(data['datetime'])
            data = data.set_index('datetime')
            
            return data
            
        except Exception as e:
            print(f"Error loading data: {e}")
            raise
    
    def run_backtest(self, **params) -> pd.Series:
        """
        Run a single backtest with specified parameters.
        
        Args:
            **params: Strategy parameters to use
            
        Returns:
            Backtest statistics
        """
        stats = self.backtest.run(**params)
        return stats
    
    def optimize_parameters(self, 
                          maximize: str = 'Return [%]',
                          **param_ranges) -> pd.Series:
        """
        Optimize strategy parameters.
        
        Args:
            maximize: Metric to maximize
            **param_ranges: Parameter ranges to optimize over
            
        Returns:
            Optimized parameters and results
        """
        if not param_ranges:
            param_ranges = self.strategy_class.get_optimization_params()
            
        opt_stats = self.backtest.optimize(
            maximize=maximize,
            **param_ranges
        )
        return opt_stats
    
    def monte_carlo_simulation(self, 
                             num_simulations: int = 1000,
                             **params) -> Dict:
        """
        Run Monte Carlo simulation to assess strategy robustness.
        
        Args:
            num_simulations: Number of simulations to run
            **params: Strategy parameters to use
            
        Returns:
            Simulation statistics
        """
        returns = []
        drawdowns = []
        
        for _ in range(num_simulations):
            # Randomly sample data subset
            sample_data = self.data.sample(frac=0.8)
            
            # Run backtest on sample
            bt = Backtest(sample_data, self.strategy_class, 
                         cash=self.initial_capital, 
                         commission=self.commission)
            stats = bt.run(**params)
            
            returns.append(stats['Return [%]'])
            drawdowns.append(stats['Max. Drawdown [%]'])
        
        return {
            'mean_return': np.mean(returns),
            'median_return': np.median(returns),
            'std_return': np.std(returns),
            'mean_drawdown': np.mean(drawdowns),
            'max_drawdown': np.max(drawdowns),
            'win_rate': np.mean(np.array(returns) > 0)
        }
    
    def visualize_results(self, 
                         stats: pd.Series,
                         output_dir: str = 'results',
                         show_plot: bool = False):
        """
        Create visualizations of backtest results.
        
        Args:
            stats: Backtest statistics
            output_dir: Directory to save plots
            show_plot: Whether to display plots
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Plot equity curve
        plt.figure(figsize=(12, 6))
        plt.plot(stats._equity_curve)
        plt.title('Equity Curve')
        plt.xlabel('Date')
        plt.ylabel('Equity')
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'equity_curve.png'))
        if show_plot:
            plt.show()
        plt.close()
        
        # Plot drawdown
        plt.figure(figsize=(12, 6))
        plt.plot(stats._drawdown)
        plt.title('Drawdown')
        plt.xlabel('Date')
        plt.ylabel('Drawdown %')
        plt.grid(True)
        plt.savefig(os.path.join(output_dir, 'drawdown.png'))
        if show_plot:
            plt.show()
        plt.close()
        
        # Save statistics
        stats.to_csv(os.path.join(output_dir, 'statistics.csv'))
    
    def analyze_risk(self, stats: pd.Series) -> Dict:
        """
        Perform risk analysis on backtest results.
        
        Args:
            stats: Backtest statistics
            
        Returns:
            Risk metrics
        """
        return {
            'sharpe_ratio': stats['Return [%]'] / stats['Volatility [%]'],
            'sortino_ratio': stats['Return [%]'] / stats['Max. Drawdown [%]'],
            'calmar_ratio': stats['Return [%]'] / abs(stats['Max. Drawdown [%]']),
            'win_rate': stats['Win Rate [%]'] / 100,
            'profit_factor': stats['Profit Factor'],
            'expectancy': stats['Return [%]'] * stats['Win Rate [%]'] / 100
        } 