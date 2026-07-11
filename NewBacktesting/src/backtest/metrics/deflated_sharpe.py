"""
Deflated Sharpe Ratio.

Based on: Bailey, Lopez de Prado — The Deflated Sharpe Ratio.
"""
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd
from scipy import stats


class DeflatedSharpeRatio:
    """
    Calculate deflated Sharpe ratio to adjust for multiple testing.
    """
    def __init__(
        self,
        returns: pd.Series,
        n_trials: int = 100,
        risk_free_rate: float = 0.0
    ):
        """
        Initialize deflated Sharpe ratio.
        
        Args:
            returns: Strategy returns
            n_trials: Number of trials/strategies tested
            risk_free_rate: Annual risk-free rate
        """
        self.returns = returns
        self.n_trials = n_trials
        self.risk_free_rate = risk_free_rate
    
    def calculate(self) -> Dict[str, Any]:
        """
        Calculate deflated Sharpe ratio.
        
        Returns:
            Dictionary with results
        """
        # Calculate moments
        mean = self.returns.mean()
        std = self.returns.std()
        skew = self.returns.skew()
        kurt = self.returns.kurtosis()
        
        # Annualize
        ann_mean = mean * 365.25
        ann_std = std * np.sqrt(365.25)
        
        # Sharpe ratio
        if ann_std == 0:
            sharpe = 0
        else:
            sharpe = (ann_mean - self.risk_free_rate) / ann_std
        
        # Calculate variance of Sharpe ratio
        n = len(self.returns)
        if n <= 1:
            sr_variance = 0
        else:
            sr_variance = (1 + 0.5 * sharpe**2 - skew * sharpe + 0.25 * (kurt - 3) * sharpe**2) / (n - 1)
        
        # Deflated Sharpe using Bonferroni correction for simplicity
        if sr_variance <= 0:
            deflated_sharpe = sharpe
            p_value = 1.0
        else:
            # Adjust for multiple testing
            alpha_bonferroni = 0.05 / self.n_trials
            z_alpha = stats.norm.ppf(1 - alpha_bonferroni)
            deflated_sharpe = sharpe - z_alpha * np.sqrt(sr_variance)
            
            # P-value
            z_score = sharpe / np.sqrt(sr_variance) if sr_variance > 0 else 0
            p_value = 2 * (1 - stats.norm.cdf(abs(z_score)))
        
        return {
            "sharpe_ratio": sharpe,
            "deflated_sharpe_ratio": deflated_sharpe,
            "n_trials": self.n_trials,
            "n_observations": n,
            "mean": mean,
            "std": std,
            "skewness": skew,
            "kurtosis": kurt,
            "sharpe_ratio_variance": sr_variance,
            "p_value": p_value
        }
