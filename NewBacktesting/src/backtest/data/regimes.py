"""
Market regime detection for analysis and backtesting.
"""
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
try:
    from sklearn.cluster import KMeans
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class MarketRegimeDetector:
    """
    Detects market regimes using clustering.
    """
    def __init__(
        self,
        data: pd.DataFrame,
        n_regimes: int = 3,
        window_size: int = 50
    ):
        self.data = data
        self.n_regimes = n_regimes
        self.window_size = window_size
        
    def detect(self) -> Dict[str, Any]:
        """
        Detect market regimes.
        
        Returns:
            Dictionary with regime information
        """
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not available"}
            
        if len(self.data) < self.window_size + self.n_regimes:
            return {"error": "insufficient data"}
            
        # Calculate features
        features = []
        for i in range(self.window_size, len(self.data)):
            window = self.data.iloc[i - self.window_size:i]
            returns = window["close"].pct_change().dropna()
            
            volatility = returns.std()
            mean_return = returns.mean()
            skewness = returns.skew() if len(returns) > 3 else 0
            kurtosis = returns.kurtosis() if len(returns) > 3 else 3
            
            price_momentum = (window["close"].iloc[-1] / window["close"].iloc[0]) - 1
            
            volume_mean = window["volume"].mean() if "volume" in window.columns else 0
            volume_std = window["volume"].std() if "volume" in window.columns else 0
            
            features.append([
                volatility, mean_return, skewness, kurtosis,
                price_momentum, volume_mean, volume_std
            ])
            
        # Cluster
        kmeans = KMeans(n_clusters=self.n_regimes, random_state=42)
        regime_labels = kmeans.fit_predict(np.array(features))
        
        # Create regime series
        regime_series = pd.Series(index=self.data.index, dtype=int)
        regime_series.iloc[self.window_size:] = regime_labels
        
        # Calculate regime stats
        regime_stats = {}
        for regime in range(self.n_regimes):
            mask = regime_series == regime
            regime_data = self.data[mask]
            
            if len(regime_data) > 0:
                returns = regime_data["close"].pct_change().dropna()
                regime_stats[f"regime_{regime}"] = {
                    "count": len(regime_data),
                    "percentage": (len(regime_data) / len(self.data)) * 100,
                    "mean_return": returns.mean() if len(returns) > 0 else 0,
                    "volatility": returns.std() if len(returns) > 0 else 0,
                    "sharpe": (returns.mean() / returns.std()) if (len(returns) > 0 and returns.std() > 0) else 0
                }
                
        return {
            "n_regimes": self.n_regimes,
            "window_size": self.window_size,
            "regimes": regime_series.fillna(-1).astype(int).to_dict(),
            "regime_stats": regime_stats
        }
