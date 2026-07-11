"""
Volume breakout strategy migrated from the legacy backup set.
"""
import pandas as pd

from backtest.strategies.base import Strategy


class VolumeBreakout(Strategy):
    """
    Enter when volume spikes and price breaks out of a consolidation range.
    """

    def __init__(self, params: dict = None):
        super().__init__(params)
        self.consolidation_period = self.params.get("consolidation_period", 20)
        self.volume_multiplier = self.params.get("volume_multiplier", 2.0)

    def generate_signals(self) -> pd.DataFrame:
        if self.data is None:
            raise ValueError("Strategy data has not been set. Call set_data() before generate_signals().")
        df = self.data.copy()
        df["volume_sma"] = df["volume"].rolling(self.consolidation_period).mean()
        df["high_range"] = df["high"].rolling(self.consolidation_period).max()
        df["low_range"] = df["low"].rolling(self.consolidation_period).min()
        df["signal"] = 0

        for idx in range(self.consolidation_period, len(df)):
            volume_spike = df.iloc[idx]["volume"] > (df.iloc[idx - 1]["volume_sma"] * self.volume_multiplier)
            price_range = df.iloc[idx]["high_range"] - df.iloc[idx]["low_range"]
            if price_range <= 0:
                continue
            if df.iloc[idx]["close"] > df.iloc[idx]["high_range"] and volume_spike:
                df.at[df.index[idx], "signal"] = 1
            elif df.iloc[idx]["close"] < df.iloc[idx]["low_range"] and volume_spike:
                df.at[df.index[idx], "signal"] = -1

        return df[["signal"]]
