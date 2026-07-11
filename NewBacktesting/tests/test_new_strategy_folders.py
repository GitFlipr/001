import unittest

import pandas as pd

from strategies.breakout import BreakoutMomentumBand, BreakoutRetest, BreakoutVolumeSpike
from strategies.mean_reversion import MeanReversionBounce, MeanReversionPullback, MeanReversionRange
from strategies.momentum import MomentumAcceleration, MomentumStrength, MomentumWake
from strategies.scalping import ScalpingPulse, ScalpingQuickRev, ScalpingVolatility
from strategies.seasonality import SeasonalityWindow, SeasonalRange, SeasonalTilt
from strategies.trend_following import TrendPulse, TrendRibbon, TrendSlope
from strategies.volume import VolumeFlowBreak, VolumePressure, VolumeSurge
from strategies.misc import MiscBias, MiscCountertrend, MiscSwing
from strategies.misc_experimental import ExperimentalBlend, ExperimentalMeanReversion, ExperimentalMomentum
from strategies.volatility_risk import VolatilityCandle, VolatilityCompression, VolatilityRange
from strategies.breakout_channel import ChannelBreakout, ChannelMomentum, ChannelRetest
from strategies.seasonality_calendar import CalendarBias, CalendarMomentum, CalendarRange
from strategies.volume_flow import FlowBias, FlowMomentum, FlowRange
from strategies.statistical_arbitrage import StatArbMeanReversion, StatArbMomentum, StatArbSpread


class NewStrategyFoldersTest(unittest.TestCase):
    def setUp(self):
        index = pd.date_range("2024-01-01", periods=120, freq="D")
        close = pd.Series(range(120), index=index, dtype=float) + 100.0
        self.df = pd.DataFrame(
            {
                "open": close + 0.5,
                "high": close + 1.0,
                "low": close - 1.0,
                "close": close,
                "volume": 1000.0,
            },
            index=index,
        )

    def test_new_strategy_classes_generate_signals(self):
        strategy_classes = [
            BreakoutMomentumBand,
            BreakoutRetest,
            BreakoutVolumeSpike,
            MeanReversionBounce,
            MeanReversionPullback,
            MeanReversionRange,
            MomentumAcceleration,
            MomentumStrength,
            MomentumWake,
            ScalpingPulse,
            ScalpingQuickRev,
            ScalpingVolatility,
            SeasonalityWindow,
            SeasonalRange,
            SeasonalTilt,
            TrendPulse,
            TrendRibbon,
            TrendSlope,
            VolumeFlowBreak,
            VolumePressure,
            VolumeSurge,
            MiscBias,
            MiscCountertrend,
            MiscSwing,
            ExperimentalBlend,
            ExperimentalMeanReversion,
            ExperimentalMomentum,
            VolatilityCandle,
            VolatilityCompression,
            VolatilityRange,
            ChannelBreakout,
            ChannelMomentum,
            ChannelRetest,
            CalendarBias,
            CalendarMomentum,
            CalendarRange,
            FlowBias,
            FlowMomentum,
            FlowRange,
            StatArbMeanReversion,
            StatArbMomentum,
            StatArbSpread,
        ]

        for strategy_cls in strategy_classes:
            with self.subTest(strategy_cls=strategy_cls.__name__):
                strategy = strategy_cls(params={})
                strategy.set_data(self.df)
                signals = strategy.generate_signals()
                self.assertIsInstance(signals, pd.DataFrame)
                self.assertIn("signal", signals.columns)


if __name__ == "__main__":
    unittest.main()
