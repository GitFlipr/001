from backtesting import Strategy, Backtest
import talib
import numpy as np
import pandas as pd

class SynergisticConfluence(Strategy):
    # Parameters
    ema_fast = 50
    ema_slow = 200
    rsi_period = 14
    macd_fast = 12
    macd_slow = 26
    macd_signal = 9
    atr_period = 14
    atr_multiplier_sl = 1.5
    rr_ratio = 2  # Risk:Reward 1:2
    risk_per_trade = 0.01  # 1% risk
    volume_period = 20
    confluence_threshold = 3  # Require at least 3 confirming signals
    
    def init(self):
        # Indicators using self.I() - data columns already cleaned in loading
        self.ema_fast = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_fast)
        self.ema_slow = self.I(talib.EMA, self.data.Close, timeperiod=self.ema_slow)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        self.macd, self.macd_signal, self.macd_hist = self.I(talib.MACD, self.data.Close, 
                                                              fastperiod=self.macd_fast, 
                                                              slowperiod=self.macd_slow, 
                                                              signalperiod=self.macd_signal)
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        self.volume_sma = self.I(talib.SMA, self.data.Volume, timeperiod=self.volume_period)
        
        # Simple SuperTrend approximation using ATR (basic version)
        self.supertrend = self.I(self.supertrend_calc, self.data.High, self.data.Low, self.data.Close, self.atr, multiplier=3)
        
        # Swing high/low for basic Fib approximation (using MAX/MIN)
        self.swing_high = self.I(talib.MAX, self.data.High, timeperiod=20)
        self.swing_low = self.I(talib.MIN, self.data.Low, timeperiod=20)
    
    @staticmethod
    def supertrend_calc(high, low, close, atr, multiplier=3):
        # Simple SuperTrend implementation
        high = np.asarray(high)
        low = np.asarray(low)
        close = np.asarray(close)
        atr = np.asarray(atr)
        hl2 = (high + low) / 2
        upper = hl2 + (multiplier * atr)
        lower = hl2 - (multiplier * atr)
        supertrend = np.zeros_like(close)
        direction = np.ones_like(close, dtype=int)
        # Set initial value
        supertrend[0] = lower[0]
        direction[0] = 1
        for i in range(1, len(close)):
            if close[i] > upper[i-1]:
                direction[i] = 1
            elif close[i] < lower[i-1]:
                direction[i] = -1
            else:
                direction[i] = direction[i-1]
                if direction[i] > 0 and lower[i] < lower[i-1]:
                    lower[i] = lower[i-1]
                if direction[i] < 0 and upper[i] > upper[i-1]:
                    upper[i] = upper[i-1]
            if direction[i] > 0:
                supertrend[i] = lower[i]
            else:
                supertrend[i] = upper[i]
        return supertrend
    
    def next(self):
        # Current values
        price = self.data.Close[-1]
        atr_val = self.atr[-1]
        if np.isnan(atr_val) or atr_val == 0:
            return  # Skip if invalid
        
        # Basic market structure
        uptrend = self.ema_fast[-1] > self.ema_slow[-1] and price > self.ema_fast[-1]
        downtrend = self.ema_fast[-1] < self.ema_slow[-1] and price < self.ema_fast[-1]
        
        # Approximate Fib retracement (simple: distance from recent swing)
        if len(self.swing_high) > 20 and not np.isnan(self.swing_high[-2]) and not np.isnan(self.swing_low[-2]):
            recent_high = self.swing_high[-2]
            recent_low = self.swing_low[-2]
            fib_range = recent_high - recent_low
            if fib_range > 0:
                fib_382 = recent_high - 0.382 * fib_range
                fib_618 = recent_high - 0.618 * fib_range
                near_fib_support = price <= fib_382 or price > recent_low * 1.01  # Pullback to support
                near_fib_resistance = price >= fib_618 or price < recent_high * 0.99
            else:
                near_fib_support = False
                near_fib_resistance = False
        else:
            recent_high = np.nan
            recent_low = np.nan
            near_fib_support = False
            near_fib_resistance = False
        
        # Confluence signals for Long
        long_signals = 0
        # 1. Trend: Uptrend structure
        if uptrend:
            long_signals += 1
            print(f"🌙 Long Signal 1: Uptrend confirmed (EMA50 > EMA200 & price > EMA50) 🚀")
        # 2. Pullback to Fib/support
        if near_fib_support:
            long_signals += 1
            print(f"✨ Long Signal 2: Near Fib 0.382 support zone 🌙")
        # 3. Momentum: MACD bullish
        if self.macd[-1] > self.macd_signal[-1] and self.macd_hist[-1] > 0:
            long_signals += 1
            print(f"📈 Long Signal 3: MACD bullish crossover & positive histogram 🚀")
        # 4. Oscillator: RSI oversold bounce
        if len(self.rsi) > 1 and self.rsi[-1] < 40 and self.rsi[-1] > self.rsi[-2]:  # Bounce from oversold
            long_signals += 1
            print(f"🔥 Long Signal 4: RSI oversold bounce (<40) 🌙")
        # 5. Volume confirmation
        if self.data.Volume[-1] > self.volume_sma[-1] * 1.2:
            long_signals += 1
            print(f"💥 Long Signal 5: Volume surge > SMA 🚀")
        # 6. SuperTrend green (below price)
        if price > self.supertrend[-1]:
            long_signals += 1
            print(f"🌟 Long Signal 6: SuperTrend bullish (price > ST) ✨")
        
        # Long Entry if confluence >= threshold and no long position
        if self.position.size <= 0 and long_signals >= self.confluence_threshold:
            sl_distance = atr_val * self.atr_multiplier_sl
            risk_amount = self.equity * self.risk_per_trade
            position_size = int(round(risk_amount / sl_distance))  # Units of BTC
            sl_price = price - sl_distance
            tp_price = price + (sl_distance * self.rr_ratio)
            if position_size > 0 and sl_price < price < tp_price:
                self.buy(size=position_size, limit=price, sl=sl_price, tp=tp_price)
                print(f"🚀 MOON DEV LONG ENTRY: Price={price:.2f}, Size={position_size}, SL={sl_price:.2f}, TP={tp_price:.2f}, Signals={long_signals} 🌙")
            else:
                print(f"🌙 DEBUG: Skipping LONG - Invalid size/SL/TP: size={position_size}, SL={sl_price:.2f}, TP={tp_price:.2f} ✨")
        
        # Confluence signals for Short
        short_signals = 0
        # 1. Trend: Downtrend structure
        if downtrend:
            short_signals += 1
            print(f"🌙 Short Signal 1: Downtrend confirmed (EMA50 < EMA200 & price < EMA50) 🚀")
        # 2. Pullback to Fib/resistance
        if near_fib_resistance:
            short_signals += 1
            print(f"✨ Short Signal 2: Near Fib 0.618 resistance zone 🌙")
        # 3. Momentum: MACD bearish
        if self.macd[-1] < self.macd_signal[-1] and self.macd_hist[-1] < 0:
            short_signals += 1
            print(f"📉 Short Signal 3: MACD bearish crossover & negative histogram 🚀")
        # 4. Oscillator: RSI overbought drop
        if len(self.rsi) > 1 and self.rsi[-1] > 60 and self.rsi[-1] < self.rsi[-2]:  # Drop from overbought
            short_signals += 1
            print(f"🔥 Short Signal 4: RSI overbought drop (>60) 🌙")
        # 5. Volume confirmation
        if self.data.Volume[-1] > self.volume_sma[-1] * 1.2:
            short_signals += 1
            print(f"💥 Short Signal 5: Volume surge > SMA 🚀")
        # 6. SuperTrend red (above price)
        if price < self.supertrend[-1]:
            short_signals += 1
            print(f"🌟 Short Signal 6: SuperTrend bearish (price < ST) ✨")
        
        # Short Entry if confluence >= threshold and no short position
        if self.position.size >= 0 and short_signals >= self.confluence_threshold:
            sl_distance = atr_val * self.atr_multiplier_sl
            risk_amount = self.equity * self.risk_per_trade
            position_size = int(round(risk_amount / sl_distance))  # Units of BTC
            sl_price = price + sl_distance
            tp_price = price - (sl_distance * self.rr_ratio)
            if position_size > 0 and tp_price < price < sl_price:
                self.sell(size=position_size, limit=price, sl=sl_price, tp=tp_price)
                print(f"🚀 MOON DEV SHORT ENTRY: Price={price:.2f}, Size={position_size}, SL={sl_price:.2f}, TP={tp_price:.2f}, Signals={short_signals} 🌙")
            else:
                print(f"🌙 DEBUG: Skipping SHORT - Invalid size/SL/TP: size={position_size}, SL={sl_price:.2f}, TP={tp_price:.2f} ✨")
        
        # Early exit on trend change (SuperTrend flip)
        if self.position.size > 0 and price < self.supertrend[-1]:
            self.position.close()
            print(f"🌙 Early LONG EXIT: SuperTrend flip against trade 🚀")
        if self.position.size < 0 and price > self.supertrend[-1]:
            self.position.close()
            print(f"🌙 Early SHORT EXIT: SuperTrend flip against trade 🚀")

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
    data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})

    bt = Backtest(data, SynergisticConfluence, cash=1_000_000, commission=0.002)
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
    results = test_on_all_data(SynergisticConfluence, 'SynergisticConfluence', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")