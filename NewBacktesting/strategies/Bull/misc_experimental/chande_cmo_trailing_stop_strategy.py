import pandas as pd
import numpy as np
import talib
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

class ImprovedChandeCMOStrategy(Strategy):
    """
    Improved Chande CMO Strategy with manual trailing stop logic:
    - Uses ATR to set and update a trailing stop after entering a position.
    - The trailing stop is managed manually:
        * For long positions: trail_stop = max(previous_trail_stop, current_close - ATR * multiplier)
        * For short positions: trail_stop = min(previous_trail_stop, current_close + ATR * multiplier)
    - If the price crosses the trailing stop, the position is closed.
    """
    # Default parameters (can be tuned or optimized)
    cmo_period = 9
    overbought = 50
    oversold = -50
    atr_period = 14
    atr_multiplier_stop = 2.0  # ATR-based trailing stop multiplier

    def init(self):
        # Calculate CMO
        self.cmo = self.I(talib.CMO, self.data.Close, timeperiod=self.cmo_period)
        # Calculate ATR for volatility-based risk management
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)

        # Initialize a variable to hold our manual trailing stop level
        self.trail_stop = None

    def next(self):
        if len(self.cmo) < 2:
            return

        prev_cmo = self.cmo[-2]
        curr_cmo = self.cmo[-1]
        atr_value = self.atr[-1]
        current_close = self.data.Close[-1]

        # Update / Check Trailing Stop for Existing Positions
        if self.position.is_long:
            # Update trailing stop for long position
            new_trail = current_close - atr_value * self.atr_multiplier_stop
            # If we don't have a trail_stop yet, set it
            if self.trail_stop is None:
                self.trail_stop = new_trail
            else:
                # Adjust trailing stop only upwards
                if new_trail > self.trail_stop:
                    self.trail_stop = new_trail

            # If price goes below the trail stop, close the position
            if current_close < self.trail_stop:
                self.position.close()
                self.trail_stop = None

        elif self.position.is_short:
            # Update trailing stop for short position
            new_trail = current_close + atr_value * self.atr_multiplier_stop
            # If we don't have a trail_stop yet, set it
            if self.trail_stop is None:
                self.trail_stop = new_trail
            else:
                # Adjust trailing stop only downwards (since it's a short)
                if new_trail < self.trail_stop:
                    self.trail_stop = new_trail

            # If price goes above the trail stop, close the position
            if current_close > self.trail_stop:
                self.position.close()
                self.trail_stop = None
        else:
            # No position open, reset trail_stop
            self.trail_stop = None

        # --- EXIT CONDITIONS ---
        # Exit Long: If we are long and CMO, after being above +50, now crosses back below +50
        if self.position.is_long and prev_cmo > self.overbought and curr_cmo < self.overbought:
            self.position.close()
            self.trail_stop = None

        # Exit Short: If we are short and CMO, after being below -50, now crosses back above -50
        if self.position.is_short and prev_cmo < self.oversold and curr_cmo > self.oversold:
            self.position.close()
            self.trail_stop = None

        # --- ENTRY CONDITIONS ---
        # Buy Entry: CMO was below -50 and now crosses above -50
        if prev_cmo < self.oversold and curr_cmo > self.oversold:
            # Close any short positions and go long
            if self.position.is_short:
                self.position.close()
            if not self.position:
                self.buy()  # Trail stop will be set in the next iteration once the position is open

        # Sell Entry: CMO was above +50 and now crosses below +50
        if prev_cmo > self.overbought and curr_cmo < self.overbought:
            # Close any long positions and go short
            if self.position.is_long:
                self.position.close()
            if not self.position:
                self.sell()  # Trail stop will be set in the next iteration once the position is open
