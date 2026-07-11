"""
Top-level strategy registry.

Imports every strategy from every sub-package so that discovery only needs
to scan this one module.  Sub-packages handle their own lazy loading and
error isolation — if a sub-package fails to import it is skipped silently.
"""
from __future__ import annotations

import importlib
from pathlib import Path

# Sub-packages to aggregate (order doesn't matter for discovery)
_SUBPACKAGES = [
    "trend_following",
    "mean_reversion",
    "breakout",
    "breakout_channel",
    "scalping",
    "momentum",
    "misc",
    "misc_experimental",
    "volatility_risk",
    "volume",
    "volume_flow",
    "statistical_arbitrage",
    "seasonality",
    "seasonality_calendar",
    "Bear",
    "Bull",
    "Neutral",
    "HighVolatility",
    "LowVolatility",
    "StatisticalArbitrage",
    "Moon",
]

_loaded: dict = {}

for _pkg in _SUBPACKAGES:
    try:
        _mod = importlib.import_module(f".{_pkg}", __name__)
        for _name in getattr(_mod, "__all__", []):
            _obj = getattr(_mod, _name, None)
            if _obj is not None and _name not in _loaded:
                _loaded[_name] = _obj
    except Exception:
        pass

globals().update(_loaded)

__all__ = sorted(_loaded.keys())
