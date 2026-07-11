# Strategy Migration Progress

## Completed
- Added a reusable strategy base adapter under the new backtesting package.
- Migrated the following legacy-style strategies into the new package:
  - Trend following: EMA crossover, SMA crossover
  - Mean reversion: RSI mean reversion
  - Breakout: Bollinger breakout
  - Scalping: Bull/Bear EMA + RSI scalping
- Added a smoke-test file for import and signal-generation checks.

## Remaining work
- Port additional strategies from the old backup folder into the matching subpackages:
  - momentum
  - seasonality
  - volume
  - misc
- Keep the legacy strategy names intact where possible to reduce friction.

## Quick import examples
```python
from strategies.trend_following import EMACrossover, SMACrossover
from strategies.mean_reversion import RSIMeanReversion
from strategies.breakout import BollingerBreakout
from strategies.scalping import BullBearEMARsiScalping
```
