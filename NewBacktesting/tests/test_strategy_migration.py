import pandas as pd

from strategies import BullBearEMARsiScalping
from strategies.trend_following import EMACrossover, SMACrossover
from strategies.mean_reversion import RSIMeanReversion
from strategies.breakout import BollingerBreakout


def build_sample_frame():
    index = pd.date_range("2024-01-01", periods=120, freq="D")
    close = pd.Series(range(120), index=index, dtype=float) + 100.0
    df = pd.DataFrame(
        {
            "open": close + 0.5,
            "high": close + 1.0,
            "low": close - 1.0,
            "close": close,
            "volume": 1000.0,
        },
        index=index,
    )
    return df


def test_migrated_strategies_generate_signals():
    data = build_sample_frame()

    for strategy_cls in [EMACrossover, SMACrossover, RSIMeanReversion, BollingerBreakout, BullBearEMARsiScalping]:
        strategy = strategy_cls(params={})
        strategy.set_data(data)
        signals = strategy.generate_signals()
        assert isinstance(signals, pd.DataFrame)
        assert "signal" in signals.columns
