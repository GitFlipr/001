"""Trend Following Strategies Registry"""
from .ema_crossover import EMACrossover, EMACrossoverRegime
from .macd_strategy import MACDStrategy
from .adx_trend import ADXTrend
from .golden_death_cross_200 import GoldenDeathCross

__all__ = [
    'EMACrossover',
    'EMACrossoverRegime', 
    'MACDStrategy',
    'ADXTrend',
    'GoldenDeathCross',
]
