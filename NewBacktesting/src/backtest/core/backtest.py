"""
Core backtesting engine with vectorized operations
"""
from pathlib import Path
from typing import Dict, Any, Optional, Type

import pandas as pd
import numpy as np
from ..data.loader import DataLoader
from ..strategies.base import Strategy
from ..metrics.metrics import Metrics
from backtest.config import get_default_results_dir


class Backtest:
    """
    High-performance backtesting engine using vectorized operations
    """
    def __init__(
        self,
        data: pd.DataFrame,
        strategy: Type[Strategy],
        initial_capital: float = 10000.0,
        commission: float = 0.001,
        slippage: float = 0.0
    ):
        """
        Initialize backtest
        
        Args:
            data: DataFrame with OHLCV data
            strategy: Strategy class to backtest
            initial_capital: Starting capital
            commission: Commission rate per trade (percentage)
            slippage: Slippage per trade (percentage)
        """
        self.data = data.copy()
        self.strategy_class = strategy
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.strategy = None
        self.results = None

    def save_results(self, output_dir: Optional[Path] = None, filename: str = "backtest_results.parquet") -> Path:
        output_path = Path(output_dir or get_default_results_dir())
        output_path.mkdir(parents=True, exist_ok=True)
        result_file = output_path / filename
        if self.results is None:
            raise ValueError("No backtest results available. Run the backtest first.")
        self.results["data"].to_parquet(result_file, index=True)
        return result_file

    def run(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the backtest
        
        Args:
            params: Strategy parameters
            
        Returns:
            Dictionary with backtest results
        """
        # Initialize strategy
        self.strategy = self.strategy_class(params or {})
        self.strategy.set_data(self.data)
        
        # Generate signals
        signals = self.strategy.generate_signals()
        
        # Calculate positions and returns
        self.results = self._calculate_backtest(signals)
        
        return self.results

    def _calculate_backtest(self, signals: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate backtest results from signals using vectorized operations
        
        Args:
            signals: DataFrame with 'signal' column
            
        Returns:
            Dictionary with results
        """
        # Make a copy of data
        df = self.data.copy()
        
        # Add signals
        df["signal"] = signals["signal"]
        
        # Calculate position changes (entry/exit)
        df["position"] = df["signal"].ffill().fillna(0)
        df["position_change"] = df["position"].diff().fillna(0)
        
        # Calculate trade prices with slippage
        df["trade_price"] = df["close"]
        # Long entry: buy at ask (close + slippage)
        long_entry_mask = df["position_change"] > 0
        df.loc[long_entry_mask, "trade_price"] = df["close"] * (1 + self.slippage)
        # Long exit: sell at bid (close - slippage)
        long_exit_mask = (df["position_change"] < 0) & (df["position"].shift(1) > 0)
        df.loc[long_exit_mask, "trade_price"] = df["close"] * (1 - self.slippage)
        # Short entry: sell at bid (close - slippage)
        short_entry_mask = df["position_change"] < 0
        df.loc[short_entry_mask, "trade_price"] = df["close"] * (1 - self.slippage)
        # Short exit: buy at ask (close + slippage)
        short_exit_mask = (df["position_change"] > 0) & (df["position"].shift(1) < 0)
        df.loc[short_exit_mask, "trade_price"] = df["close"] * (1 + self.slippage)
        
        # Calculate daily returns from price changes
        df["price_return"] = df["close"].pct_change().fillna(0)
        
        # Calculate strategy returns (position * price_return)
        df["strategy_return"] = df["position"].shift(1) * df["price_return"]
        
        # Calculate transaction costs
        df["transaction_cost"] = 0.0
        # Commission on position changes
        df.loc[df["position_change"] != 0, "transaction_cost"] = (
            abs(df["position_change"]) * self.commission
        )
        
        # Net strategy returns after costs
        df["strategy_return_net"] = df["strategy_return"] - df["transaction_cost"]
        
        # Calculate equity curve
        df["equity"] = self.initial_capital * (1 + df["strategy_return_net"]).cumprod()
        
        # Benchmark equity (buy and hold)
        df["benchmark_equity"] = self.initial_capital * (1 + df["price_return"]).cumprod()
        
        # Extract trades first
        trades_list = self._extract_trades(df)
        
        # Calculate metrics
        metrics_calc = Metrics(df["strategy_return_net"], trades=trades_list)
        metrics = metrics_calc.calculate_all()
        
        # Compile results
        results = {
            "data": df,
            "equity_curve": df["equity"],
            "benchmark_equity": df["benchmark_equity"],
            "returns": df["strategy_return_net"],
            "benchmark_returns": df["price_return"],
            "metrics": metrics,
            "trades": trades_list
        }
        
        return results

    def _extract_trades(self, df: pd.DataFrame) -> list[dict]:
        """
        Extract individual trades from backtest data using vectorized operations
        
        Args:
            df: DataFrame with backtest results
            
        Returns:
            List of trade dictionaries
        """
        # Find entry and exit points using vectorized operations
        position_change = df["position_change"].values
        position = df["position"].values
        trade_prices = df["trade_price"].values
        indices = df.index
        
        trades = []
        current_position = 0
        entry_price = 0
        entry_idx = None
        
        for i in range(len(df)):
            if current_position == 0 and position_change[i] != 0:
                # Enter position
                current_position = position[i]
                entry_price = trade_prices[i]
                entry_idx = i
            elif current_position != 0 and position_change[i] != 0:
                # Exit position
                exit_price = trade_prices[i]
                exit_idx = i
                
                if current_position > 0:
                    # Long trade
                    profit_pct = (exit_price - entry_price) / entry_price
                else:
                    # Short trade
                    profit_pct = (entry_price - exit_price) / entry_price
                
                trades.append({
                    "entry_date": indices[entry_idx],
                    "exit_date": indices[exit_idx],
                    "entry_price": entry_price,
                    "exit_price": exit_price,
                    "position": current_position,
                    "profit_pct": profit_pct,
                    "return_pct": profit_pct,
                    "profit": profit_pct * self.initial_capital
                })
                
                current_position = 0
                entry_price = 0
                entry_idx = None
        
        return trades
