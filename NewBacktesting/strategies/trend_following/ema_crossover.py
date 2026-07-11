import pandas as pd

from backtest.strategies.base import Strategy
from backtest.utils.indicators import ema, crossover


class EMACrossover(Strategy):
    """Simple EMA crossover strategy using the migrated base interface."""

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.fast_period = self.params.get("fast_period", 9)
        self.slow_period = self.params.get("slow_period", 20)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["ema_fast"] = ema(df["close"], self.fast_period)
        df["ema_slow"] = ema(df["close"], self.slow_period)
        df["signal"] = 0
        df.loc[crossover(df["ema_fast"], df["ema_slow"]) > 0, "signal"] = 1
        df.loc[crossover(df["ema_fast"], df["ema_slow"]) < 0, "signal"] = -1
        return df[["signal"]]


class EMACrossoverRegime(EMACrossover):
    """Compatibility alias for regime-style EMA crossover."""

    pass
