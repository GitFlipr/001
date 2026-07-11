"""Bear regime strategies."""
from .bear_strategies import (
    BearEMAShort,
    BearRSIOverextended,
    BearBreakdownPullback,
    BearMACDMomentum,
)

__all__ = [
    "BearEMAShort",
    "BearRSIOverextended",
    "BearBreakdownPullback",
    "BearMACDMomentum",
]
