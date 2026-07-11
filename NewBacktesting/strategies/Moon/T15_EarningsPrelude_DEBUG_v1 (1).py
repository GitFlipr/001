from backtesting import Strategy, Backtest
import talib
import pandas as pd
import numpy as np

class EarningsPrelude(Strategy):
    # 🌙 Moon Dev's EarningsPrelude Strategy 🚀
    # Adapted for technical signals mimicking pre-earnings momentum
    # Entry: Above 20 SMA, RSI>50, Volume>1.5x 10-period avg, Bullish candle (Close>Open)
    # Exit: TP +3%, SL -1.5%, or below SMA
    # Risk: 1% of equity per trade
    # Position size based on risk to SL

    risk_per_trade = 0.01  # 1% risk
    stop_loss_pct = 0.015  # 1.5% SL
    take_profit_pct = 0.03  # 3% TP

    def init(self):
        # Technical indicators using TA-Lib
        self.sma20 = self.I(talib.SMA, self.data.Close, timeperiod=20)
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=14)
        self.avgvol10 = self.I(talib.SMA, self.data.Volume, timeperiod=10)
        
        # Debug print
        print("🌙 EarningsPrelude initialized with SMA20, RSI14, Vol10 ✨")

    def next(self):
        current_price = self.data.Close[-1]
        current_volume = self.data.Volume[-1]
        current_open = self.data.Open[-1]
        current_rsi = self.rsi[-1]
        current_sma = self.sma20[-1]
        current_avgvol = self.avgvol10[-1]

        # Skip if indicators not ready
        if np.isnan(current_sma) or np.isnan(current_rsi) or np.isnan(current_avgvol):
            return

        # Exit rules
        if self.position:
            # Exit if below SMA (trend break)
            if current_price < current_sma:
                self.position.close()
                print(f"🌙 Exit on SMA break at {self.data.index[-1]}, Price: {current_price} 📉")
                return
            
            # Calculate profit_pct using last trade's entry_price
            if self.trades:
                entry_price = self.trades[-1].entry_price
                profit_pct = (current_price - entry_price) / entry_price
                
                # Note: SL and TP handled by order, but can add custom here if needed
                # For trailing: if profit >1%, trail by 1% (simple check)
                if profit_pct > 0.01:
                    trail_price = current_price * 0.99
                    if current_price < trail_price:
                        self.position.close()
                        print(f"🌙 Trailing stop hit at {self.data.index[-1]}, Price: {current_price} 📉")
                        return

        # Entry rules (long only)
        else:
            # Conditions: Above SMA, RSI>50, High volume, Bullish candle
            if (current_price > current_sma and
                current_rsi > 50 and
                current_volume > 1.5 * current_avgvol and
                current_price > current_open):

                # Calculate position size based on risk
                risk_amount = self.equity * self.risk_per_trade
                risk_per_unit = current_price * self.stop_loss_pct
                if risk_per_unit > 0:
                    position_size = risk_amount / risk_per_unit
                    position_size = int(round(position_size))
                    
                    if position_size > 0:
                        sl_price = current_price * (1 - self.stop_loss_pct)
                        tp_price = current_price * (1 + self.take_profit_pct)
                        
                        self.buy(size=position_size, sl=sl_price, tp=tp_price)
                        print(f"🌙 EarningsPrelude Entry 🚀 at {self.data.index[-1]}, Price: {current_price}, Size: {position_size}, SL: {sl_price}, TP: {tp_price} 💰")

# 🌙 MOON DEV'S MULTI-DATA TESTING FRAMEWORK 🚀
# Tests this strategy on 25+ data sources automatically!
if __name__ == "__main__":
    import sys
    import os
    from backtesting import Backtest
    import pandas as pd

    # Data cleaning as per requirements
    data = pd.read_csv('/Users/md/Dropbox/dev/github/moon-dev-ai-agents-for-trading/src/data/rbi/BTC-USD-15m.csv')
    data.columns = data.columns.str.strip().str.lower()  # Clean names
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])  # Drop unnamed
    data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'}, inplace=True)
    data = data.set_index(pd.to_datetime(data['datetime']))

    # FIRST: Run standard backtest and print stats (REQUIRED for parsing!)
    print("\n🌙 Running initial backtest for stats extraction...")
    bt = Backtest(data, EarningsPrelude, cash=1_000_000, commission=0.002)
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
    results = test_on_all_data(EarningsPrelude, 'EarningsPrelude', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")