import talib
from backtesting import Strategy, Backtest
import pandas as pd
import numpy as np

class CascadeWeighting(Strategy):
    ema_period = 20
    rsi_period = 14
    atr_period = 14
    vol_period = 10
    adx_period = 14
    max_cascade_entries = 3
    max_bars_for_cascade = 10
    volume_multiplier = 1.5
    risk_percent = 0.01
    tp_multiplier_full = 2.0
    tp_multiplier_low = 1.5
    weight_threshold = 0.6
    pause_bars = 20
    adx_threshold = 25

    def init(self):
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.vol_avg = self.I(talib.SMA, self.data.Volume, timeperiod=self.vol_period)
        self.adx = self.I(talib.ADX, self.data.High, self.data.Low, self.data.Close, timeperiod=self.adx_period)
        
        self.last_trend = None
        self.current_cascade_entries = 0
        self.cascade_profitable = 0
        self.cascade_total = 0
        self.consecutive_losses = 0
        self.paused = False
        self.pause_start = 0
        self.last_entry_bar = -self.max_bars_for_cascade
        self.prev_trades_len = 0
        self.initial_cash = self._broker._cash

    def is_bullish_engulfing(self):
        if len(self.data) < 2:
            return False
        o1, c1 = self.data.Open[-2], self.data.Close[-2]
        o2, c2 = self.data.Open[-1], self.data.Close[-1]
        return (c1 < o1) and (o2 <= c1) and (c2 >= o1) and (c2 > o2)

    def is_bearish_engulfing(self):
        if len(self.data) < 2:
            return False
        o1, c1 = self.data.Open[-2], self.data.Close[-2]
        o2, c2 = self.data.Open[-1], self.data.Close[-1]
        return (c1 > o1) and (o2 >= c1) and (c2 <= o1) and (c2 < o2)

    def get_recent_high(self, lookback=5):
        if len(self.data) < lookback + 1:
            return self.data.High[-1]
        return max(self.data.High[-lookback-1:-1])

    def get_recent_low(self, lookback=5):
        if len(self.data) < lookback + 1:
            return self.data.Low[-1]
        return min(self.data.Low[-lookback-1:-1])

    def calculate_weight(self, is_initial, direction):
        if is_initial:
            return 1.0
        if self.cascade_total == 0:
            return 1.0
        success_rate = (self.cascade_profitable / self.cascade_total) * 0.8
        # Alignment: 1.0 if position profitable and trend intact, else 0.5
        alignment = 1.0
        if self.position:
            if (direction > 0 and self.position.pl <= 0) or (direction < 0 and self.position.pl <= 0):
                alignment = 0.5
        else:
            alignment = 0.5
        return success_rate * alignment

    def next(self):
        current_bar = len(self.data)
        current_price = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        current_ema = self.ema[-1]
        current_rsi = self.rsi[-1]
        current_atr_raw = self.atr[-1]
        if np.isnan(current_atr_raw):
            current_atr = 1e-6
            print(f"🌙 CascadeWeighting: NaN ATR detected, using fallback 1e-6 for calculations ✨")
        else:
            current_atr = max(current_atr_raw, 1e-6)
        current_adx = self.adx[-1]

        current_trend = 'up' if current_price > current_ema else 'down'
        direction = 1 if current_trend == 'up' else -1

        # Reset cascade on trend change
        if self.last_trend != current_trend:
            self.current_cascade_entries = 0
            self.cascade_profitable = 0
            self.cascade_total = 0
            self.last_trend = current_trend
            self.last_entry_bar = -self.max_bars_for_cascade
            print(f"🌙 CascadeWeighting: New trend detected - {current_trend} ✨")

        # Check for newly closed trades
        if len(self.trades) > self.prev_trades_len:
            last_trade = self.trades[-1]
            if last_trade.is_long and current_trend == 'up' or not last_trade.is_long and current_trend == 'down':
                self.cascade_total += 1
                if last_trade.pl > 0:
                    self.cascade_profitable += 1
                    self.consecutive_losses = 0
                    print(f"🌙 CascadeWeighting: Profitable trade closed! PnL: {last_trade.pl:.2f} 🚀")
                else:
                    self.consecutive_losses += 1
                    print(f"🌙 CascadeWeighting: Loss trade closed! PnL: {last_trade.pl:.2f} 😔")
            self.prev_trades_len = len(self.trades)

        # Pause logic
        if self.paused:
            if current_bar - self.pause_start > self.pause_bars:
                self.paused = False
                self.consecutive_losses = 0
                print(f"🌙 CascadeWeighting: Resume trading after pause! 🌙")
            return

        if self.consecutive_losses >= 3:
            self.paused = True
            self.pause_start = current_bar
            print(f"🌙 CascadeWeighting: Pausing trading after 3 consecutive losses! 🛑")
            return

        # Global exit on trend reversal
        if self.position:
            if (self.position.is_long and current_price < current_ema) or (not self.position.is_long and current_price > current_ema):
                self.position.close()
                print(f"🌙 CascadeWeighting: Global exit on trend reversal! Exit at {current_price:.2f} 💥")
                # Reset cascade entries on full exit if trend changed
                if len(self.trades) == self.prev_trades_len:  # No new trade opened
                    self.current_cascade_entries = 0
                    self.last_entry_bar = -self.max_bars_for_cascade

        # Entry logic
        is_long_signal = self.is_bullish_engulfing() or (current_price > self.get_recent_high(5))
        is_short_signal = self.is_bearish_engulfing() or (current_price < self.get_recent_low(5))
        volume_confirm = current_volume > self.volume_multiplier * self.vol_avg[-1]

        can_cascade = current_adx >= self.adx_threshold
        bars_since_entry = current_bar - self.last_entry_bar

        # Long entry
        if direction > 0 and volume_confirm and current_rsi < 70:
            is_initial_long = not self.position or self.position.is_short
            if is_initial_long:
                signal = is_long_signal
                allow_cascade = True  # Initial always allowed
            else:
                signal = is_long_signal
                allow_cascade = can_cascade and bars_since_entry <= self.max_bars_for_cascade and self.current_cascade_entries < self.max_cascade_entries
            if signal and allow_cascade and not self.paused:
                weight = max(0.0, self.calculate_weight(is_initial_long, 1))
                if weight >= self.weight_threshold or is_initial_long:
                    if current_atr <= 0:
                        print(f"🌙 CascadeWeighting: Skipping LONG entry due to invalid ATR: {current_atr_raw} ✨")
                    else:
                        risk_amount = self.initial_cash * self.risk_percent * weight
                        entry_price = current_price
                        sl_price = entry_price - current_atr
                        risk_per_unit = entry_price - sl_price
                        num_units = risk_amount / risk_per_unit
                        size = int(round(num_units))
                        tp_mult_raw = self.tp_multiplier_full if weight >= 0.8 else self.tp_multiplier_low
                        tp_mult = max(tp_mult_raw, 0.1)
                        tp_price = entry_price + (tp_mult * current_atr)
                        print(f"🌙 Debug LONG: weight={weight:.2f}, atr={current_atr:.2f}, tp_mult={tp_mult:.2f}, sl={sl_price:.2f}, tp={tp_price:.2f}, size={size} ✨")
                        if sl_price < current_price < tp_price and size > 0:
                            self.buy(size=size, limit=entry_price, sl=sl_price, tp=tp_price)
                            self.current_cascade_entries += 1
                            self.last_entry_bar = current_bar
                            print(f"🌙 CascadeWeighting: Entering LONG at {entry_price:.2f}, weight={weight:.2f}, size={size}, SL={sl_price:.2f}, TP={tp_price:.2f} 🚀")
                        else:
                            print(f"🌙 CascadeWeighting: Skipping invalid LONG order: SL={sl_price:.5f} < Price={current_price:.5f} < TP={tp_price:.5f}? {sl_price < current_price < tp_price}, size={size} ⚠️")

        # Short entry
        elif direction < 0 and volume_confirm and current_rsi > 30:
            is_initial_short = not self.position or self.position.is_long
            if is_initial_short:
                signal = is_short_signal
                allow_cascade = True
            else:
                signal = is_short_signal
                allow_cascade = can_cascade and bars_since_entry <= self.max_bars_for_cascade and self.current_cascade_entries < self.max_cascade_entries
            if signal and allow_cascade and not self.paused:
                weight = max(0.0, self.calculate_weight(is_initial_short, -1))
                if weight >= self.weight_threshold or is_initial_short:
                    if current_atr <= 0:
                        print(f"🌙 CascadeWeighting: Skipping SHORT entry due to invalid ATR: {current_atr_raw} ✨")
                    else:
                        risk_amount = self.initial_cash * self.risk_percent * weight
                        entry_price = current_price
                        sl_price = entry_price + current_atr
                        risk_per_unit = sl_price - entry_price
                        num_units = risk_amount / risk_per_unit
                        size = int(round(num_units))
                        tp_mult_raw = self.tp_multiplier_full if weight >= 0.8 else self.tp_multiplier_low
                        tp_mult = max(tp_mult_raw, 0.1)
                        tp_price = entry_price - (tp_mult * current_atr)
                        print(f"🌙 Debug SHORT: weight={weight:.2f}, atr={current_atr:.2f}, tp_mult={tp_mult:.2f}, sl={sl_price:.2f}, tp={tp_price:.2f}, size={size} ✨")
                        if tp_price < current_price < sl_price and size > 0:
                            self.sell(size=size, limit=entry_price, sl=sl_price, tp=tp_price)
                            self.current_cascade_entries += 1
                            self.last_entry_bar = current_bar
                            print(f"🌙 CascadeWeighting: Entering SHORT at {entry_price:.2f}, weight={weight:.2f}, size={size}, SL={sl_price:.2f}, TP={tp_price:.2f} 🚀")
                        else:
                            print(f"🌙 CascadeWeighting: Skipping invalid SHORT order: TP={tp_price:.5f} < Price={current_price:.5f} < SL={sl_price:.5f}? {tp_price < current_price < sl_price}, size={size} ⚠️")

# 🌙 MOON DEV'S MULTI-DATA TESTING FRAMEWORK 🚀
# Tests this strategy on 25+ data sources automatically!
if __name__ == "__main__":
    import sys
    import os
    from backtesting import Backtest
    import pandas as pd

    # FIRST: Run standard backtest and print stats (REQUIRED for parsing!)
    print("\n🌙 Running initial backtest for stats extraction...")
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data = data.set_index(pd.to_datetime(data['datetime']))
    data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)

    bt = Backtest(data, CascadeWeighting, cash=1_000_000, commission=0.002)
    stats = bt.run()

    # 🌙 CRITICAL: Print full stats for Moon Dev's parser!
    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS (Moon Dev's Format)")
    print("="*80)
    print(stats)
    print("="*80 + "\n")

    # THEN: Run multi-data testing
    sys.path.append('/Users/md/Dropbox/dev/github/moon-dev-trading-bots/backtests')
    from multi_data_tester import test_on_all_data

    print("\n" + "="*80)
    print("🚀 MOON DEV'S MULTI-DATA BACKTEST - Testing on 25+ Data Sources!")
    print("="*80)

    # Test this strategy on all configured data sources
    # This will test on: BTC, ETH, SOL (multiple timeframes), AAPL, TSLA, ES, NQ, GOOG, NVDA
    # IMPORTANT: verbose=False to prevent plotting (causes timeouts in parallel processing!)
    results = test_on_all_data(CascadeWeighting, 'CascadeWeighting', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")