"""
Visualization tools for backtesting results
"""
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False


class Visualizer:
    """
    Create plots from backtest results
    """
    def __init__(self, results: Dict[str, Any]):
        """
        Initialize with backtest results
        
        Args:
            results: Dictionary of backtest results from Backtest.run()
        """
        self.results = results
        self.data = results["data"]
        self.equity = results["equity_curve"]
        self.benchmark = results["benchmark_equity"]
        self.metrics = results["metrics"]
        self.trades = results["trades"]

    def plot_equity_curve(self, save_path: Optional[str] = None):
        """
        Plot equity curve vs benchmark
        
        Args:
            save_path: Optional path to save figure
        """
        if not PLOTLY_AVAILABLE:
            print("Plotly not installed. Install with: pip install plotly")
            return

        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=("Equity Curve", "Drawdown"),
            row_heights=[0.7, 0.3]
        )

        # Equity curve
        fig.add_trace(
            go.Scatter(
                x=self.equity.index,
                y=self.equity,
                name="Strategy",
                line=dict(color="blue", width=2)
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=self.benchmark.index,
                y=self.benchmark,
                name="Buy & Hold",
                line=dict(color="gray", width=2, dash="dash")
            ),
            row=1, col=1
        )

        # Drawdown
        rolling_max = self.equity.cummax()
        drawdown = (self.equity - rolling_max) / rolling_max * 100
        fig.add_trace(
            go.Scatter(
                x=drawdown.index,
                y=drawdown,
                name="Drawdown",
                fill="tozeroy",
                line=dict(color="red", width=1),
                fillcolor="rgba(255, 0, 0, 0.3)"
            ),
            row=2, col=1
        )

        fig.update_layout(
            title="Backtest Results",
            xaxis_title="Date",
            yaxis_title="Equity",
            yaxis2_title="Drawdown (%)",
            height=700,
            showlegend=True
        )

        if save_path:
            fig.write_html(save_path)
        else:
            fig.show()

    def plot_trades(self, save_path: Optional[str] = None):
        """
        Plot trades on price chart
        
        Args:
            save_path: Optional path to save figure
        """
        if not PLOTLY_AVAILABLE:
            print("Plotly not installed. Install with: pip install plotly")
            return

        fig = go.Figure()

        # Price chart
        fig.add_trace(
            go.Candlestick(
                x=self.data.index,
                open=self.data["open"],
                high=self.data["high"],
                low=self.data["low"],
                close=self.data["close"],
                name="Price"
            )
        )

        # Trades
        if len(self.trades) > 0:
            # Long entries
            long_entries = self.trades[self.trades["position"] > 0]
            fig.add_trace(
                go.Scatter(
                    x=long_entries["entry_date"],
                    y=long_entries["entry_price"],
                    mode="markers",
                    name="Long Entry",
                    marker=dict(color="green", size=10, symbol="triangle-up")
                )
            )
            # Long exits
            fig.add_trace(
                go.Scatter(
                    x=long_entries["exit_date"],
                    y=long_entries["exit_price"],
                    mode="markers",
                    name="Long Exit",
                    marker=dict(color="red", size=10, symbol="triangle-down")
                )
            )
            # Short entries
            short_entries = self.trades[self.trades["position"] < 0]
            fig.add_trace(
                go.Scatter(
                    x=short_entries["entry_date"],
                    y=short_entries["entry_price"],
                    mode="markers",
                    name="Short Entry",
                    marker=dict(color="red", size=10, symbol="triangle-down")
                )
            )
            # Short exits
            fig.add_trace(
                go.Scatter(
                    x=short_entries["exit_date"],
                    y=short_entries["exit_price"],
                    mode="markers",
                    name="Short Exit",
                    marker=dict(color="green", size=10, symbol="triangle-up")
                )
            )

        fig.update_layout(
            title="Trades on Price Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            height=600
        )

        if save_path:
            fig.write_html(save_path)
        else:
            fig.show()
