import talib
import pandas as pd
from backtesting import Strategy, Backtest

class NicheConcentration(Strategy):
    ema_period = 20
    rsi_period = 14
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    atr_period = 14
    vol_period = 10
    risk_pct = 0.01  # 1% risk per trade
    rr_ratio = 2  # 2:1 risk-reward
    atr_multiplier_sl = 1.5
    vol_multiplier = 1.5
    
    def init(self):
        self.bar_count = 0
        self.ema = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_period)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.macd, self.signal, self.hist = self.I(talib.MACD, self.data.Close, 
                                                   fastperiod=self.macd_fast, 
                                                   slowperiod=self.macd_slow, 
                                                   signalperiod=self.macd_signal)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.vol_avg = self.I(talib.SMA, self.data.Volume, timeperiod=self.vol_period)
        print("✨ Indicators initialized for NicheConcentration strategy 🌙")
    
    def next(self):
        self.bar_count += 1
        current_close = self.data.Close[-1]
        prev_close = self.data.Close[-2]
        current_ema = self.ema[-1]
        prev_ema = self.ema[-2]
        current_rsi = self.rsi[-1]
        current_hist = self.hist[-1]
        prev_hist = self.hist[-2]
        current_vol = self.data.Volume[-1]
        current_vol_avg = self.vol_avg[-1]
        current_atr = self.atr[-1]
        
        # Long Entry: Breakout above EMA, RSI > 50, Volume > 1.5x avg
        long_breakout = current_close > current_ema and prev_close <= prev_ema
        long_conditions = (
            long_breakout and
            current_rsi > 50 and
            current_vol > self.vol_multiplier * current_vol_avg
        )
        
        if self.position.is_short or self.position.size == 0:
            if long_conditions:
                entry_price = current_close
                if pd.isna(current_atr) or current_atr <= 0:
                    print("🌙 Invalid ATR for long entry, skipping ✨")
                else:
                    sl_distance = self.atr_multiplier_sl * current_atr
                    sl_price = entry_price - sl_distance
                    tp_price = entry_price + (self.rr_ratio * sl_distance)
                    # Technical fix: Ensure strict SL < entry < TP with small epsilon for precision
                    epsilon = 1e-4
                    sl_price = min(sl_price, entry_price - epsilon)
                    tp_price = max(tp_price, entry_price + epsilon)
                    risk_distance_pct = sl_distance / entry_price
                    if risk_distance_pct > 0 and not pd.isna(risk_distance_pct):
                        risk_amount = self.equity * self.risk_pct
                        position_value = risk_amount / risk_distance_pct
                        size = int(round(position_value / entry_price))
                        if size > 0 and sl_price < entry_price < tp_price:
                            self.buy(size=size, limit=entry_price, sl=sl_price, tp=tp_price)
                            print(f"🚀 🌙 LONG ENTRY: Size={size}, Entry={entry_price:.2f}, SL={sl_price:.2f}, TP={tp_price:.2f} ✨")
                    else:
                        print("🌙 Invalid risk distance for long, skipping ✨")
        
        # Short Entry: Breakdown below EMA, bearish MACD hist divergence, Volume > 1.5x avg
        short_breakdown = current_close < current_ema and prev_close >= prev_ema
        bearish_div = current_hist < prev_hist  # Simplified divergence
        short_conditions = (
            short_breakdown and
            current_rsi < 50 and  # Added RSI <50 for short
            bearish_div and
            current_vol > self.vol_multiplier * current_vol_avg
        )
        
        if self.position.is_long or self.position.size == 0:
            if short_conditions:
                entry_price = current_close
                if pd.isna(current_atr) or current_atr <= 0:
                    print("🌙 Invalid ATR for short entry, skipping ✨")
                else:
                    sl_distance = self.atr_multiplier_sl * current_atr
                    sl_price = entry_price + sl_distance
                    tp_price = entry_price - (self.rr_ratio * sl_distance)
                    # Technical fix: Ensure strict TP < entry < SL with small epsilon for precision
                    epsilon = 1e-4
                    sl_price = max(sl_price, entry_price + epsilon)
                    tp_price = min(tp_price, entry_price - epsilon)
                    risk_distance_pct = sl_distance / entry_price
                    if risk_distance_pct > 0 and not pd.isna(risk_distance_pct):
                        risk_amount = self.equity * self.risk_pct
                        position_value = risk_amount / risk_distance_pct
                        size = int(round(position_value / entry_price))
                        if size > 0 and tp_price < entry_price < sl_price:
                            self.sell(size=size, limit=entry_price, sl=sl_price, tp=tp_price)
                            print(f"🔻 🌙 SHORT ENTRY: Size={size}, Entry={entry_price:.2f}, SL={sl_price:.2f}, TP={tp_price:.2f} ✨")
                    else:
                        print("🌙 Invalid risk distance for short, skipping ✨")
        
        # Debug position status every 100 bars
        if self.bar_count % 100 == 0 and self.position.size != 0:
            side = 'Long' if self.position.is_long else 'Short'
            print(f"📊 Position: {side}, Size: {self.position.size}, PL: {self.position.pl:.2f} 🌙 at bar {self.bar_count}")

# 🌙 MOON DEV'S MULTI-DATA TESTING FRAMEWORK 🚀
# Tests this strategy on 25+ data sources automatically!
if __name__ == "__main__":
    import sys
    import os
    from backtesting import Backtest
    import pandas as pd

    # Data cleaning as per requirements
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    # Clean column names: strip and lower (though already clean)
    data.columns = data.columns.str.strip().str.lower()
    # Drop unnamed columns
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    # Ensure required columns with proper case
    data = data.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume'
    })
    # Set datetime as index per requirements
    data = data.set_index(pd.to_datetime(data['datetime']))

    # FIRST: Run standard backtest and print stats (REQUIRED for parsing!)
    print("\n🌙 Running initial backtest for stats extraction...")
    bt = Backtest(data, NicheConcentration, cash=1_000_000, commission=0.002, trade_on_close=True)
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
    results = test_on_all_data(NicheConcentration, 'NicheConcentration', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")