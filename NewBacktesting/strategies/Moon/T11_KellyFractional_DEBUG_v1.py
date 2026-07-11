from backtesting import Strategy
import pandas as pd
import numpy as np

class KellyFractional(Strategy):
    window = 3000
    kelly_factor = 0.5
    rebalance_days = 30

    def init(self):
        def compute_returns_mean(closes, window):
            closes_series = pd.Series(closes)
            returns = closes_series.pct_change()
            return returns.rolling(window=window).mean().values
        
        self.mu = self.I(compute_returns_mean, self.data.Close, window=self.window)
        
        def compute_returns_var(closes, window):
            closes_series = pd.Series(closes)
            returns = closes_series.pct_change()
            return returns.rolling(window=window).var().values
        
        self.s2 = self.I(compute_returns_var, self.data.Close, window=self.window)
        
        self.last_rebalance = None
        print("🌙 KellyFractional initialized with rolling window of {} periods 🚀".format(self.window))

    def next(self):
        if pd.isna(self.mu[-1]) or pd.isna(self.s2[-1]):
            return  # Not enough data for indicators
        
        current_time = self.data.index[-1]
        rebalance = False
        if self.last_rebalance is None:
            rebalance = True
        else:
            delta_days = (current_time - self.last_rebalance).days
            if delta_days >= self.rebalance_days:
                rebalance = True
        
        if rebalance:
            mu = self.mu[-1]
            s2 = self.s2[-1]
            if s2 <= 0 or mu <= 0:
                f = 0.0
            else:
                f = self.kelly_factor * (mu / s2)
            f = min(max(f, 0.0), 1.0)
            
            # Close current position if any
            if self.position:
                self.position.close()
                print(f"🌙 KellyFractional: Closed position at {current_time} 💸")
            
            # Calculate and open new position
            if f > 0:
                equity = self._broker.equity
                price = self.data.Close[-1]
                desired_shares = int(round(f * equity / price))
                if desired_shares > 0:
                    self.buy(size=desired_shares)
                    print(f"🌙 KellyFractional: Rebalanced LONG f={f:.4f}, mu={mu:.6f}, s2={s2:.6f}, shares={desired_shares} at {current_time} 🚀")
                else:
                    print(f"🌙 KellyFractional: f={f:.4f} but no shares at {current_time} ⚠️")
            else:
                print(f"🌙 KellyFractional: Deallocated to cash (f={f:.4f}) at {current_time} ✨")
            
            self.last_rebalance = current_time

# 🌙 MOON DEV'S MULTI-DATA TESTING FRAMEWORK 🚀
# Tests this strategy on 25+ data sources automatically!
if __name__ == "__main__":
    import sys
    import os
    from backtesting import Backtest
    import pandas as pd

    # Data cleaning as per instructions
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data = data.set_index(pd.to_datetime(data['datetime']))

    # FIRST: Run standard backtest and print stats (REQUIRED for parsing!)
    print("\n🌙 Running initial backtest for stats extraction...")
    bt = Backtest(data, KellyFractional, cash=1_000_000, commission=0.002)
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
    results = test_on_all_data(KellyFractional, 'KellyFractional', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")