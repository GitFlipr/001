# New Trading Strategies

This document describes the new trading strategies added to the framework.

## Trend Following Strategies

### TripleEMATrend (`trend_following/triple_ema_trend.py`)
- **Concept**: Uses three EMAs (fast, medium, slow) for robust trend confirmation
- **Entry**: When all three EMAs align bullishly/bearishly
- **Exit**: When alignment breaks
- **Parameters**: 
  - `fast_period`: 9 (default)
  - `medium_period`: 21 (default)
  - `slow_period`: 50 (default)

### VWMATrend (`trend_following/vwma_trend.py`)
- **Concept**: Volume-Weighted Moving Average trend following
- **Entry**: Price crosses VWMA with volume surge confirmation
- **Exit**: Price crosses back or volume dries up
- **Parameters**:
  - `vwma_period`: 20 (default)
  - `volume_ma_period`: 20 (default)
  - `volume_threshold`: 1.2 (default)

### KeltnerTrend (`trend_following/keltner_trend.py`)
- **Concept**: Keltner Channel breakout trend following
- **Entry**: Price breaks out of channel in trend direction
- **Exit**: Price crosses middle EMA or opposite channel
- **Parameters**:
  - `ema_period`: 20 (default)
  - `atr_period`: 10 (default)
  - `atr_multiplier`: 2.0 (default)

## Mean Reversion Strategies

### BollingerMeanReversion (`mean_reversion/bollinger_mean_reversion.py`)
- **Concept**: Classic mean reversion using Bollinger Band extremes
- **Entry**: Price touches bands with RSI confirmation
- **Exit**: Price reaches middle band
- **Parameters**:
  - `bb_period`: 20 (default)
  - `bb_std`: 2.0 (default)
  - `rsi_period`: 14 (default)
  - `rsi_oversold`: 30 (default)
  - `rsi_overbought`: 70 (default)

### StochMeanReversion (`mean_reversion/stoch_mean_reversion.py`)
- **Concept**: Stochastic RSI mean reversion with SMA trend filter
- **Entry**: Stoch RSI crosses back from extreme levels
- **Exit**: Stoch RSI reaches middle zone
- **Parameters**:
  - `rsi_period`: 14 (default)
  - `stoch_period`: 14 (default)
  - `smooth_k`: 3 (default)
  - `smooth_d`: 3 (default)
  - `oversold`: 20 (default)
  - `overbought`: 80 (default)
  - `ma_period`: 50 (default)

## Breakout Strategies

### BBVolumeBreakout (`breakout/bb_volume_breakout_adapter.py`)
- **Concept**: Bollinger Bands breakout with volume confirmation
- **Entry**: Price breaks out of BB with volume surge
- **Exit**: Price crosses back inside bands
- **Parameters**:
  - `bb_period`: 20 (default)
  - `bb_std`: 2.0 (default)
  - `volume_ma_period`: 20 (default)
  - `volume_threshold`: 1.5 (default)

## Momentum Strategies

### ROCMomentum (`momentum/roc_momentum.py`)
- **Concept**: Pure momentum using Rate of Change indicator
- **Entry**: ROC crosses threshold with trend confirmation
- **Exit**: ROC crosses back toward zero
- **Parameters**:
  - `roc_period`: 12 (default)
  - `momentum_threshold`: 5.0 (default)
  - `ma_period`: 50 (default)

## Scalping Strategies

### EMARSIScalp (`scalping/ema_rsi_scalp.py`)
- **Concept**: Fast EMA crossovers with RSI filter
- **Entry**: EMA cross with RSI not at extremes
- **Exit**: Opposite EMA cross
- **Parameters**:
  - `fast_ema`: 5 (default)
  - `slow_ema`: 13 (default)
  - `rsi_period`: 7 (default)
  - `rsi_overbought`: 75 (default)
  - `rsi_oversold`: 25 (default)

## Volatility Risk Strategies

### ATRVolatility (`volatility_risk/atr_volatility.py`)
- **Concept**: ATR-based volatility regime detection
- **Entry**: Volatility expansion with trend confirmation
- **Exit**: Volatility contraction
- **Parameters**:
  - `atr_period`: 14 (default)
  - `atr_ma_period`: 20 (default)
  - `volatility_threshold`: 1.5 (default)
  - `ma_period`: 50 (default)

## Volume Flow Strategies

### VWMAVolumeFlow (`volume_flow/vwma_volume.py`)
- **Concept**: VWMA with volume flow analysis
- **Entry**: Price crosses VWMA with strong volume flow
- **Exit**: Price crosses back or volume flow reverses
- **Parameters**:
  - `vwma_period`: 20 (default)
  - `volume_ma_period`: 20 (default)
  - `volume_bull_threshold`: 1.3 (default)
  - `volume_bear_threshold`: 1.2 (default)

## Usage Example

```python
from backtest.strategies.base import Strategy
from strategies.trend_following.triple_ema_trend import TripleEMATrend

# Create strategy with custom parameters
strategy = TripleEMATrend(params={
    "fast_period": 12,
    "medium_period": 26,
    "slow_period": 60
})

# Set data and generate signals
strategy.set_data(ohlcv_dataframe)
signals = strategy.generate_signals()
```

## Best Practices

1. **Parameter Optimization**: Use the optimization utilities to find optimal parameters for your specific asset
2. **Risk Management**: Always combine with proper position sizing and stop-loss rules
3. **Backtesting**: Test across multiple market regimes before live deployment
4. **Combination**: Consider combining multiple strategies for diversification
