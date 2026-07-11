import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple

class StrategyBacktester:
    def __init__(self, strategy_class, data_path: str, config_grid: Dict = None):
        """
        Initialize the backtester with a strategy class and configuration options.
        
        Args:
            strategy_class (class): Trading strategy class to backtest
            data_path (str): Path to the price data CSV file
            config_grid (dict): Dictionary of parameters to test
        """
        self.strategy_class = strategy_class
        self.data_path = data_path
        
        # Default configuration grid if not provided
        self.config_grid = config_grid or {
            'trix_period': [10, 15, 20],
            'stoch_period': [10, 14, 18],
            'stoch_smooth_period': [3, 5, 7],
            'profit_target': [0.01, 0.02, 0.03],
            'stop_loss': [0.01, 0.02, 0.03]
        }
        
        # Load price data
        self.price_data = self._load_price_data()
    
    def _load_price_data(self) -> pd.DataFrame:
        """
        Load price data from CSV, with fallback to sample data generation.
        
        Returns:
            pandas.DataFrame: Price data with 'close', 'high', 'low' columns
        """
        try:
            price_data = pd.read_csv(self.data_path)
            required_columns = ['close', 'high', 'low']
            
            # Validate required columns
            if not all(col in price_data.columns for col in required_columns):
                raise ValueError(f"Missing required columns: {required_columns}")
            
            return price_data
        
        except (FileNotFoundError, ValueError) as e:
            print(f"Data loading error: {e}. Generating sample data...")
            np.random.seed(42)
            dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
            
            return pd.DataFrame({
                'date': dates,
                'close': np.cumsum(np.random.randn(len(dates))) + 50000,
                'high': np.cumsum(np.random.randn(len(dates))) + 50100,
                'low': np.cumsum(np.random.randn(len(dates))) + 49900
            })
    
    def parameter_optimization(self) -> List[Dict]:
        """
        Perform grid search optimization of strategy parameters.
        
        Returns:
            List of performance dictionaries for each parameter combination
        """
        from itertools import product
        
        results = []
        total_combinations = np.prod([len(v) for v in self.config_grid.values()])
        print(f"Total parameter combinations to test: {total_combinations}")
        
        for params in product(*self.config_grid.values()):
            config = dict(zip(self.config_grid.keys(), params))
            
            strategy = self.strategy_class(
                data=self.price_data,
                trix_period=config['trix_period'],
                stoch_period=config['stoch_period'],
                stoch_smooth_period=config['stoch_smooth_period'],
                profit_target=config['profit_target'],
                stop_loss=config['stop_loss']
            )
            
            performance = strategy.detailed_analysis()
            performance.update(config)
            results.append(performance)
        
        return sorted(results, key=lambda x: x['total_return_percent'], reverse=True)
    
    def visualize_parameter_impact(self, results: List[Dict], output_dir: str = 'results'):
        """
        Create visualizations to understand parameter impact on strategy performance.
        
        Args:
            results (List[Dict]): Performance results from parameter optimization
            output_dir (str): Directory to save visualization plots
        """
        os.makedirs(output_dir, exist_ok=True)
        results_df = pd.DataFrame(results)
        
        # Correlations between parameters and performance
        performance_params = ['trix_period', 'stoch_period', 'stoch_smooth_period', 
                              'profit_target', 'stop_loss', 'total_return_percent', 
                              'win_rate']
        
        plt.figure(figsize=(12, 10))
        correlation_matrix = results_df[performance_params].corr()
        sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
        plt.title('Parameter Impact on Strategy Performance')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, 'parameter_correlation.png'))
        plt.close()
        
        # Top 10 parameter configurations
        top_configs = results_df.nlargest(10, 'total_return_percent')
        top_configs.to_csv(os.path.join(output_dir, 'top_10_configurations.csv'), index=False)
    
    def monte_carlo_simulation(self, best_config: Dict, num_simulations: int = 1000):
        """
        Perform Monte Carlo simulation to assess strategy robustness.
        
        Args:
            best_config (Dict): Best performing configuration
            num_simulations (int): Number of random simulations to run
        """
        simulation_results = []
        
        for _ in range(num_simulations):
            # Randomly sample data subset
            sample_data = self.price_data.sample(frac=0.8)
            
            strategy = self.strategy_class(
                data=sample_data,
                **best_config
            )
            
            performance = strategy.detailed_analysis()
            simulation_results.append(performance['total_return_percent'])
        
        # Analyze simulation results
        print("\nMonte Carlo Simulation Results:")
        print(f"Mean Return: {np.mean(simulation_results):.2f}%")
        print(f"Median Return: {np.median(simulation_results):.2f}%")
        print(f"Standard Deviation: {np.std(simulation_results):.2f}%")
        print(f"95% Confidence Interval: [{np.percentile(simulation_results, 2.5):.2f}%, {np.percentile(simulation_results, 97.5):.2f}%]")

def main():
    from oscillator_scalping import OscillatorScalpingStrategy
    
    # Sample usage of backtester
    backtester = StrategyBacktester(
        strategy_class=OscillatorScalpingStrategy,
        data_path='your_price_data.csv'
    )
    
    # Run parameter optimization
    optimization_results = backtester.parameter_optimization()
    
    # Visualize parameter impacts
    backtester.visualize_parameter_impact(optimization_results)
    
    # Select best configuration and run Monte Carlo simulation
    best_config = optimization_results[0]
    print("\nBest Configuration:")
    for key, value in best_config.items():
        print(f"{key}: {value}")
    
    backtester.monte_carlo_simulation(best_config)

# Backtesting Best Practices & Recommendations
"""
1. Data Quality
- Use high-quality, clean historical price data
- Include transaction costs and slippage in simulations
- Validate data integrity before backtesting

2. Avoid Overfitting
- Use walk-forward analysis
- Test on out-of-sample data
- Implement robust parameter selection methods

3. Risk Management
- Set realistic initial capital
- Use appropriate position sizing
- Consider drawdown and maximum loss scenarios

4. Continuous Improvement
- Regularly update and refine strategy
- Monitor changing market conditions
- Adapt strategy parameters dynamically
"""
