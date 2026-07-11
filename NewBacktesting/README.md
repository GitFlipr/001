# NewBacktesting

A modern, modular, high-performance backtesting framework for trading strategies.

## Features

- **Vectorized Backtesting**: Fast backtesting using pandas vectorized operations
- **Modular Design**: Clean, extensible architecture
- **Strategy Base Class**: Easy to implement custom strategies
- **Comprehensive Metrics**: Sharpe ratio, drawdown, win rate, and more
- **Visualization**: Plot equity curves, drawdowns, and trades
- **Low Latency**: Optimized for performance

## Installation

```bash
cd NewBacktesting
pip install -r requirements.txt
```

## Quick Start

```python
from backtest import Backtest, DataLoader
from examples.sma_crossover import SMACrossover
import pandas as pd

# Load your data
data = DataLoader.from_csv("path/to/your/data.csv")

# Create and run backtest
backtest = Backtest(
    data=data,
    strategy=SMACrossover,
    initial_capital=10000.0,
    commission=0.001,
    slippage=0.001
)

results = backtest.run(params={"short_window": 10, "long_window": 50})

# Print metrics
print(results["metrics"])

# Plot results
from backtest import Visualizer
viz = Visualizer(results)
viz.plot_equity_curve()
```

## Project Structure

```
NewBacktesting/
├── src/
│   └── backtest/
│       ├── __init__.py          # Main package exports
│       ├── core/
│       │   └── backtest.py      # Core backtesting engine
│       ├── data/
│       │   └── loader.py        # Data loading and preprocessing
│       ├── metrics/
│       │   └── metrics.py       # Performance metrics calculation
│       ├── strategies/
│       │   └── base.py          # Strategy base class
│       └── utils/
│           └── visualization.py # Plotting and visualization
├── examples/
│   ├── sma_crossover.py         # Example strategy
│   └── test_backtest.py         # Test script
├── data/                        # Data directory
├── results/                     # Results directory
└── requirements.txt
```

## Creating Custom Strategies

To create a custom strategy, inherit from the `Strategy` base class and implement the `generate_signals` method:

```python
from backtest.strategies.base import Strategy
import pandas as pd

class MyStrategy(Strategy):
    def __init__(self, params: dict = None):
        super().__init__(params)
        self.my_param = self.params.get("my_param", 10)
    
    def generate_signals(self) -> pd.DataFrame:
        df = self.data.copy()
        
        # Your signal generation logic here
        # Return a DataFrame with 'signal' column (1=long, -1=short, 0=no position)
        df["signal"] = 0
        
        return df[["signal"]]
```

## License

MIT
