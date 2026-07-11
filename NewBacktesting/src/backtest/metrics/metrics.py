"""
Performance metrics calculation
"""
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class Metrics:
    """
    Calculate performance metrics for backtesting results
    """
    def __init__(
        self, 
        returns: pd.Series, 
        trades: Optional[List[Dict]] = None,
        risk_free_rate: float = 0.0
    ):
        """
        Initialize with equity curve
        
        Args:
            returns: Series of returns (pct change)
            trades: List of trade dictionaries with at least 'return_pct' key
            risk_free_rate: Annual risk-free rate
        """
        self.returns = returns
        self.trades = trades or []
        self.risk_free_rate = risk_free_rate
        self.equity_curve = (1 + returns).cumprod()

    def calculate_all(self) -> Dict[str, Any]:
        """
        Calculate all performance metrics
        
        Returns:
            Dictionary of metrics
        """
        var_hist, var_param, cvar = self.var_cvar()
        metrics = {
            "start": self.returns.index[0],
            "end": self.returns.index[-1],
            "duration": (self.returns.index[-1] - self.returns.index[0]).days,
            "total_return_pct": (self.equity_curve.iloc[-1] - 1) * 100,
            "total_return": self.equity_curve.iloc[-1] - 1,
            "annual_return_pct": self.annualized_return() * 100,
            "annual_return": self.annualized_return(),
            "volatility_pct": self.annualized_volatility() * 100,
            "volatility": self.annualized_volatility(),
            "sharpe_ratio": self.sharpe_ratio(),
            "max_drawdown_pct": self.max_drawdown() * 100,
            "max_drawdown": self.max_drawdown(),
            "max_drawdown_duration": self.max_drawdown_duration(),
            "avg_drawdown_pct": self.avg_drawdown() * 100,
            "avg_drawdown": self.avg_drawdown(),
            "calmar_ratio": self.calmar_ratio(),
            "sortino_ratio": self.sortino_ratio(),
            "omega_ratio": self.omega_ratio(),
            "ulcer_index": self.ulcer_index(),
            "sterling_ratio": self.sterling_ratio(),
            "burke_ratio": self.burke_ratio(),
            "pain_index": self.pain_index(),
            "kelly_criterion": self.kelly_criterion(),
            "var_historical_99": var_hist,
            "var_parametric_99": var_param,
            "cvar_expected_shortfall_99": cvar,
            "win_rate": self.win_rate(),
            "profit_factor": self.profit_factor(),
            "payoff_ratio": self.payoff_ratio(),
            "expectancy": self.expectancy(),
            "num_trades": self.num_trades(),
            "avg_trade_pct": self.avg_trade() * 100,
            "avg_trade": self.avg_trade(),
            "best_trade_pct": self.best_trade() * 100,
            "best_trade": self.best_trade(),
            "worst_trade_pct": self.worst_trade() * 100,
            "worst_trade": self.worst_trade(),
            "quality_score": self.quality_score()
        }
        return metrics

    def annualized_return(self) -> float:
        """Calculate annualized return (CAGR)"""
        total_days = (self.returns.index[-1] - self.returns.index[0]).days
        years = total_days / 365.25
        if years == 0:
            return 0.0
        return (self.equity_curve.iloc[-1]) ** (1 / years) - 1

    def annualized_volatility(self) -> float:
        """Calculate annualized volatility"""
        if len(self.returns) == 0:
            return 0.0
        daily_vol = self.returns.std()
        return daily_vol * np.sqrt(365.25)

    def sharpe_ratio(self) -> float:
        """Calculate Sharpe ratio"""
        ann_return = self.annualized_return()
        ann_vol = self.annualized_volatility()
        if ann_vol == 0:
            return 0.0
        return (ann_return - self.risk_free_rate) / ann_vol

    def max_drawdown(self) -> float:
        """Calculate maximum drawdown"""
        rolling_max = self.equity_curve.expanding().max()
        drawdown = (self.equity_curve - rolling_max) / rolling_max
        return drawdown.min()

    def avg_drawdown(self) -> float:
        """Calculate average drawdown"""
        rolling_max = self.equity_curve.expanding().max()
        drawdowns = (self.equity_curve - rolling_max) / rolling_max
        return np.mean(drawdowns[drawdowns < 0]) if len(drawdowns[drawdowns < 0]) > 0 else 0.0

    def max_drawdown_duration(self) -> int:
        """Calculate maximum drawdown duration in bars"""
        # Find the longest period
        rolling_max = self.equity_curve.cummax()
        under_water = self.equity_curve < rolling_max
        # Calculate durations
        durations = []
        current_duration = 0
        for is_under in under_water:
            if is_under:
                current_duration += 1
            else:
                if current_duration > 0:
                    durations.append(current_duration)
                    current_duration = 0
        if current_duration > 0:
            durations.append(current_duration)
        return max(durations) if durations else 0

    def calmar_ratio(self) -> float:
        """Calculate Calmar ratio"""
        ann_return = self.annualized_return()
        max_dd = self.max_drawdown()
        if max_dd == 0:
            return 0.0
        return ann_return / abs(max_dd)

    def sortino_ratio(self) -> float:
        """Calculate Sortino ratio"""
        downside_returns = self.returns[self.returns < 0]
        if len(downside_returns) == 0:
            return 0.0
        downside_vol = downside_returns.std() * np.sqrt(365.25)
        if downside_vol == 0:
            return 0.0
        return (self.annualized_return() - self.risk_free_rate) / downside_vol

    def omega_ratio(self, threshold: float = 0.0) -> float:
        """
        Calculate Omega ratio: sum(gains above threshold) / sum(losses below threshold)
        """
        gains = self.returns[self.returns > threshold] - threshold
        losses = threshold - self.returns[self.returns < threshold]
        sum_gains = np.sum(gains)
        sum_losses = np.sum(losses)
        return sum_gains / (sum_losses + 1e-12)

    def ulcer_index(self) -> float:
        """Calculate Ulcer Index: root-mean-square of drawdowns"""
        cum_returns = self.equity_curve - 1
        peak = np.maximum.accumulate(cum_returns)
        dd_pct = (peak - cum_returns) / (peak + 1e-10) * 100
        return np.sqrt(np.mean(dd_pct ** 2))

    def sterling_ratio(self) -> float:
        """Calculate Sterling ratio"""
        total_return = self.equity_curve.iloc[-1] - 1
        avg_dd = abs(self.avg_drawdown())
        if avg_dd == 0:
            return float('inf') if total_return > 0 else 0
        return total_return / avg_dd

    def burke_ratio(self) -> float:
        """Calculate Burke ratio"""
        total_return = self.equity_curve.iloc[-1] - 1
        max_dd = abs(self.max_drawdown())
        if max_dd == 0:
            return float('inf') if total_return > 0 else 0
        return total_return / (max_dd ** 2)

    def pain_index(self) -> float:
        """Calculate Pain Index"""
        return abs(self.avg_drawdown())

    def kelly_criterion(self) -> float:
        """Calculate Kelly Criterion"""
        if len(self.trades) == 0:
            return 0.0
        
        trade_returns = [t.get('return_pct', 0) for t in self.trades]
        win_rate = np.mean(np.array(trade_returns) > 0) if len(trade_returns) > 0 else 0
        avg_win = np.mean([r for r in trade_returns if r > 0]) if len([r for r in trade_returns if r > 0]) > 0 else 0
        avg_loss = abs(np.mean([r for r in trade_returns if r < 0])) if len([r for r in trade_returns if r < 0]) > 0 else 0

        if avg_loss == 0:
            return 0.0
        
        odds = avg_win / avg_loss
        kelly = (odds * win_rate - (1 - win_rate)) / odds
        return max(0, min(kelly, 1))  # Clamp between 0 and 1

    def var_cvar(self, confidence: float = 0.99) -> tuple[Optional[float], Optional[float], Optional[float]]:
        """
        Calculate VaR (historical and parametric) and CVaR (Expected Shortfall)
        """
        if len(self.returns) < 20:
            return None, None, None
            
        alpha = 1 - confidence
        var_hist = float(np.percentile(self.returns, alpha * 100))
        tail = self.returns[self.returns <= var_hist]
        cvar = float(np.mean(tail)) if len(tail) > 0 else var_hist
        
        var_param = None
        if SCIPY_AVAILABLE:
            mu = np.mean(self.returns)
            sigma = np.std(self.returns)
            z = stats.norm.ppf(alpha)
            var_param = float(mu + z * sigma)
            
        return var_hist, var_param, cvar

    def win_rate(self) -> float:
        """Calculate win rate of trades"""
        if len(self.trades) > 0:
            return np.mean([t.get('return_pct', 0) > 0 for t in self.trades])
        positive_returns = self.returns[self.returns > 0]
        total = len(self.returns)
        if total == 0:
            return 0.0
        return len(positive_returns) / total

    def profit_factor(self) -> float:
        """Calculate profit factor"""
        if len(self.trades) > 0:
            gross_profit = sum(t.get('return_pct', 0) for t in self.trades if t.get('return_pct', 0) > 0)
            gross_loss = abs(sum(t.get('return_pct', 0) for t in self.trades if t.get('return_pct', 0) < 0))
        else:
            gross_profit = self.returns[self.returns > 0].sum()
            gross_loss = abs(self.returns[self.returns < 0].sum())
            
        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0
        return gross_profit / gross_loss

    def payoff_ratio(self) -> float:
        """Calculate Payoff Ratio: average win / average loss"""
        if len(self.trades) > 0:
            wins = [t.get('return_pct', 0) for t in self.trades if t.get('return_pct', 0) > 0]
            losses = [abs(t.get('return_pct', 0)) for t in self.trades if t.get('return_pct', 0) < 0]
        else:
            wins = self.returns[self.returns > 0]
            losses = abs(self.returns[self.returns < 0])
            
        avg_win = np.mean(wins) if len(wins) > 0 else 0
        avg_loss = np.mean(losses) if len(losses) > 0 else 0
        
        if avg_loss == 0:
            return float('inf') if avg_win > 0 else 0
        return avg_win / avg_loss

    def expectancy(self) -> float:
        """Calculate Expectancy (average trade)"""
        if len(self.trades) > 0:
            return np.mean([t.get('return_pct', 0) for t in self.trades])
        return self.avg_trade()

    def num_trades(self) -> int:
        """Calculate number of trades"""
        return len(self.trades) if len(self.trades) > 0 else len(self.returns)

    def avg_trade(self) -> float:
        """Calculate average trade"""
        if len(self.trades) > 0:
            return np.mean([t.get('return_pct', 0) for t in self.trades])
        if len(self.returns) == 0:
            return 0.0
        return self.returns.mean()

    def best_trade(self) -> float:
        """Calculate best trade"""
        if len(self.trades) > 0:
            return max(t.get('return_pct', 0) for t in self.trades)
        return self.returns.max() if len(self.returns) > 0 else 0.0

    def worst_trade(self) -> float:
        """Calculate worst trade"""
        if len(self.trades) > 0:
            return min(t.get('return_pct', 0) for t in self.trades)
        return self.returns.min() if len(self.returns) > 0 else 0.0

    def quality_score(self) -> float:
        """Calculate comprehensive quality score (0-10)"""
        score = 0.0
        
        # Return quality (30% weight)
        total_return = self.equity_curve.iloc[-1] - 1
        if total_return > 0.2:
            score += 3.0
        elif total_return > 0.1:
            score += 2.0
        elif total_return > 0.05:
            score += 1.0
        elif total_return > 0:
            score += 0.5
        
        # Sharpe ratio quality (25% weight)
        sharpe = self.sharpe_ratio()
        if sharpe > 2.0:
            score += 2.5
        elif sharpe > 1.5:
            score += 2.0
        elif sharpe > 1.0:
            score += 1.5
        elif sharpe > 0.5:
            score += 1.0
        elif sharpe > 0:
            score += 0.5
        
        # Drawdown quality (20% weight)
        max_dd = abs(self.max_drawdown())
        if max_dd < 0.05:
            score += 2.0
        elif max_dd < 0.1:
            score += 1.5
        elif max_dd < 0.2:
            score += 1.0
        elif max_dd < 0.3:
            score += 0.5
        
        # Win rate quality (15% weight)
        win_rate = self.win_rate()
        if win_rate > 0.7:
            score += 1.5
        elif win_rate > 0.6:
            score += 1.0
        elif win_rate > 0.5:
            score += 0.5
        
        # Advanced metrics quality (10% weight)
        omega = self.omega_ratio()
        if omega > 2.0:
            score += 1.0
        elif omega > 1.5:
            score += 0.5
        
        return min(score, 10.0)  # Cap at 10
