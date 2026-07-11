import talib
import pandas as pd
import numpy as np
from backtesting import Strategy, Backtest

class BullishSqueeze(Strategy):
    bb_period = 20
    bb_std = 2.0
    sma_long = 200
    bbw_sma_period = 10
    bbw_min_period = 20
    risk_per_trade = 0.01  # 1% risk
    rr_ratio = 2  # 1:2 risk-reward

    def init(self):
        close = self.data.Close
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = self.I(
            talib.BBANDS, close, timeperiod=self.bb_period,
            nbdevup=self.bb_std, nbdevdn=self.bb_std, matype=0
        )
        self.bb_upper = bb_upper
        self.bb_middle = bb_middle
        self.bb_lower = bb_lower
        
        # BBW = Upper - Lower
        self.bbw = self.I(lambda u, l: u - l, self.bb_upper, self.bb_lower)
        
        # Indicators
        self.sma200 = self.I(talib.SMA, close, timeperiod=self.sma_long)
        self.bbw_min20 = self.I(talib.MIN, self.bbw, timeperiod=self.bbw_min_period)
        self.sma_bbw10 = self.I(talib.SMA, self.bbw, timeperiod=self.bbw_sma_period)
        
        # Debug: Print every 100 bars
        self.bar_count = 0

    def next(self):
        self.bar_count += 1
        if self.bar_count % 100 == 0:
            print(f"🌙 Moon Dev Debug [{self.bar_count}]: Close={self.data.Close[-1]:.2f}, "
                  f"BBW={self.bbw[-1]:.4f}, SMA200={self.sma200[-1]:.2f}, "
                  f"Position: {'LONG' if self.position else 'FLAT'} 🚀")
        
        # Exit logic
        if self.position:
            if self.bbw[-1] > self.sma_bbw10[-1]:
                self.position.close()
                print(f"✨ Moon Dev Exit LONG: BBW Expansion! "
                      f"BBW={self.bbw[-1]:.4f} > SMA(BBW,10)={self.sma_bbw10[-1]:.4f} 🌙")
            return
        
        # Entry logic (Long only)
        squeeze_condition = self.bbw[-1] <= self.bbw_min20[-1]
        trend_condition = self.data.Close[-1] > self.sma200[-1]
        
        if squeeze_condition and trend_condition:
            entry_price = self.data.Close[-1]  # Approximate entry (actual fill at next open)
            sl_price = self.bb_lower[-1]
            risk_dist = entry_price - sl_price
            
            if risk_dist > 0:
                risk_amount = self.equity * self.risk_per_trade
                pos_size = risk_amount / risk_dist
                pos_size = int(round(pos_size))  # Ensure integer units
                
                tp_price = entry_price + (self.rr_ratio * risk_dist)
                
                # Safety check to prevent invalid SL/TP orders
                if pos_size <= 0 or sl_price >= entry_price or tp_price <= entry_price:
                    print(f"🌙 Moon Dev Debug: Invalid trade parameters - Size={pos_size}, "
                          f"SL={sl_price:.2f} >= Entry={entry_price:.2f}, "
                          f"or TP={tp_price:.2f} <= Entry={entry_price:.2f}. Skipping! ✨")
                    return
                
                self.buy(size=pos_size, limit=entry_price, sl=sl_price, tp=tp_price)
                print(f"🚀 Moon Dev BULLISH SQUEEZE ENTRY: Long {pos_size} units @ ~{entry_price:.2f}, "
                      f"SL={sl_price:.2f} (Risk: {risk_dist:.2f}), TP={tp_price:.2f} (R:R {self.rr_ratio}:1) ✨")

# 🌙 MOON DEV'S MULTI-DATA TESTING FRAMEWORK 🚀
# Tests this strategy on 25+ data sources automatically!
if __name__ == "__main__":
    import sys
    import os
    from backtesting import Backtest
    import pandas as pd

    # Data cleaning as per policy
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data = data.set_index(pd.to_datetime(data['datetime']))
    # Map to required columns with proper case
    data = data.rename(columns={
        'open': 'Open', 'high': 'High', 'low': 'Low',
        'close': 'Close', 'volume': 'Volume'
    })

    # FIRST: Run standard backtest and print stats (REQUIRED for parsing!)
    print("\n🌙 Running initial backtest for stats extraction...")
    bt = Backtest(data, BullishSqueeze, cash=1_000_000, commission=0.002)
    stats = bt.run()

    # 🌙 CRITICAL: Print full stats for Moon Dev's parser!
    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS (Moon Dev's Format)")
    print("="*80)
    print(stats)
    print(stats._strategy)
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
    results = test_on_all_data(BullishSqueeze, 'BullishSqueeze', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")