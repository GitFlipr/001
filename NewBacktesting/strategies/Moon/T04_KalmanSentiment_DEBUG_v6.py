import sys
import os
import numpy as np
import pandas as pd
import talib
from backtesting import Strategy, Backtest
from pathlib import Path

def kalman_filter(series, Q=0.01, R=0.05):
    arr = series.copy().astype(float)
    arr[np.isnan(arr)] = 0.0
    n = len(arr)
    if n == 0:
        return arr
    filtered = np.zeros(n)
    x = arr[0]
    P = 1.0
    filtered[0] = x
    for i in range(1, n):
        x_pred = x
        P_pred = P + Q
        z = arr[i]
        y = z - x_pred
        S = P_pred + R
        K = P_pred / S
        x = x_pred + K * y
        P = (1 - K) * P_pred
        filtered[i] = x
    return filtered

def diff_func(arr):
    if len(arr) == 0:
        return arr
    return np.concatenate(([0.], np.diff(arr)))

def std_func(arr, period=30):
    s = pd.Series(arr)
    return s.rolling(window=period).std().fillna(0).values

def proxy_rate_func(close):
    s = pd.Series(close)
    return s.pct_change().fillna(0).values

def filtered_rate_func(pr, Q=0.01, R=0.05):
    return kalman_filter(pr, Q, R)

def vwap_func(high, low, close, volume, index):
    df = pd.DataFrame({
        'High': high,
        'Low': low,
        'Close': close,
        'Volume': volume
    }, index=index)
    df['typical'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['pv'] = df['typical'] * df['Volume']
    df['date'] = df.index.date
    df['cum_pv'] = df.groupby('date')['pv'].cumsum()
    df['cum_vol'] = df.groupby('date')['Volume'].cumsum()
    return (df['cum_pv'] / df['cum_vol']).values

class KalmanSentiment(Strategy):
    rsi_period = 14
    atr_period = 14
    vel_ma_period = 30
    kalman_q = 0.01
    kalman_r = 0.05
    velocity_threshold = 0.0002
    rsi_ob = 70
    rsi_os = 30
    sl_mult = 1.5
    tp_r = 2.0
    risk_pct = 0.01
    vel_std_mult = 2.0

    def init(self):
        # RSI
        self.rsi = self.I(talib.RSI, self.data.Close, timeperiod=self.rsi_period)
        
        # ATR
        self.atr = self.I(talib.ATR, self.data.High, self.data.Low, self.data.Close, timeperiod=self.atr_period)
        
        # VWAP daily
        self.vwap = self.I(vwap_func, self.data.High, self.data.Low, self.data.Close, self.data.Volume, self.data.index)
        
        # Proxy rate (pct_change as funding proxy)
        self.proxy_rate = self.I(proxy_rate_func, self.data.Close)
        
        # Filtered rate
        self.filtered_rate = self.I(filtered_rate_func, self.proxy_rate, Q=self.kalman_q, R=self.kalman_r)
        
        # Velocity
        self.velocity = self.I(diff_func, self.filtered_rate)
        
        # Velocity std for dynamic threshold
        self.vel_std = self.I(std_func, self.velocity, period=self.vel_ma_period)

    def next(self):
        if len(self.data) < max(self.rsi_period, self.atr_period, self.vel_ma_period):
            return
        
        curr_price = self.data.Close[-1]
        if not np.isfinite(curr_price):
            return
            
        curr_rsi = self.rsi[-1]
        if not np.isfinite(curr_rsi):
            return
            
        curr_vwap = self.vwap[-1]
        if not np.isfinite(curr_vwap):
            return
            
        curr_filtered = self.filtered_rate[-1]
        if not np.isfinite(curr_filtered):
            return
            
        curr_velocity = self.velocity[-1]
        if not np.isfinite(curr_velocity):
            return
            
        curr_atr = self.atr[-1]
        if not np.isfinite(curr_atr) or curr_atr <= 0:
            print(f"🌙 Invalid ATR: {curr_atr}, skipping bar 🚀")
            return
            
        curr_vel_std = self.vel_std[-1]
        if not np.isfinite(curr_vel_std):
            curr_vel_std = 0.0
            
        dynamic_threshold = self.velocity_threshold
        if curr_vel_std > 0:
            dynamic_threshold = self.vel_std_mult * curr_vel_std
        
        print(f"🌙 KalmanSentiment Update: Price={curr_price:.2f}, Velocity={curr_velocity:.6f}, Threshold={dynamic_threshold:.6f}, Filtered={curr_filtered:.6f}, RSI={curr_rsi:.2f}, ATR={curr_atr:.2f} 🚀")
        
        sl_distance = self.sl_mult * curr_atr
        risk_amount = self.equity * self.risk_pct
        if self.equity <= 0 or self.risk_pct <= 0 or not np.isfinite(risk_amount):
            return
        pos_size_calc = risk_amount / sl_distance
        if not np.isfinite(pos_size_calc) or pos_size_calc <= 0:
            return
        pos_size = int(round(pos_size_calc))
        if pos_size <= 0:
            return
        
        expected_entry = curr_price
        
        # Long signal
        long_signal = (curr_velocity > dynamic_threshold and 
                       curr_filtered > 0 and 
                       curr_rsi < self.rsi_ob and 
                       curr_price > curr_vwap)
        
        if long_signal and (not self.position or self.position.is_short):
            if self.position:
                self.position.close()
            sl = expected_entry - sl_distance
            tp = expected_entry + (self.tp_r * sl_distance)
            if not np.isfinite(sl) or not np.isfinite(tp) or not (sl < expected_entry < tp):
                print(f"🌙 Invalid levels for LONG: SL={sl:.5f}, TP={tp:.5f}, entry={expected_entry:.5f} ⚠️")
                # Skip long entry but continue to check short
            else:
                if sl < curr_price < tp:
                    print(f"🌙 Placing LONG order: size={pos_size}, sl={sl:.5f}, tp={tp:.5f}, limit approx {curr_price:.5f} ✨")
                    self.buy(size=pos_size, limit=expected_entry, sl=sl, tp=tp)
                    print(f"🌙 Entering LONG at {expected_entry:.2f}, Size={pos_size}, SL={sl:.2f}, TP={tp:.2f} ✨")
                else:
                    print(f"🌙 Skipping LONG signal: current price {curr_price:.2f} not between SL {sl:.2f} and TP {tp:.2f} ⚠️")
        
        # Short signal
        short_signal = (curr_velocity < -dynamic_threshold and 
                        curr_filtered < 0 and 
                        curr_rsi > self.rsi_os and 
                        curr_price < curr_vwap)
        
        if short_signal and (not self.position or self.position.is_long):
            if self.position:
                self.position.close()
            sl = expected_entry + sl_distance
            tp = expected_entry - (self.tp_r * sl_distance)
            if not np.isfinite(sl) or not np.isfinite(tp) or not (tp < expected_entry < sl):
                print(f"🌙 Invalid levels for SHORT: TP={tp:.5f}, SL={sl:.5f}, entry={expected_entry:.5f} ⚠️")
                # Skip short entry
            else:
                if tp < curr_price < sl:
                    print(f"🌙 Placing SHORT order: size={pos_size}, sl={sl:.5f}, tp={tp:.5f}, limit approx {curr_price:.5f} ✨")
                    self.sell(size=pos_size, limit=expected_entry, sl=sl, tp=tp)
                    print(f"🌙 Entering SHORT at {expected_entry:.2f}, Size={pos_size}, SL={sl:.2f}, TP={tp:.2f} ✨")
                else:
                    print(f"🌙 Skipping SHORT signal: current price {curr_price:.2f} not between TP {tp:.2f} and SL {sl:.2f} ⚠️")

# 🌙 MOON DEV'S MULTI-DATA TESTING FRAMEWORK 🚀
# Tests this strategy on 25+ data sources automatically!
if __name__ == "__main__":
    import sys
    import os
    from backtesting import Backtest
    import pandas as pd

    project_root = Path(__file__).resolve().parent.parent.parent.parent.parent.parent
    data_path = project_root / 'src' / 'data' / 'rbi' / 'BTC-USD-15m.csv'

    # FIRST: Run standard backtest and print stats (REQUIRED for parsing!)
    print("\n🌙 Running initial backtest for stats extraction...")
    print(f"🌙 Loading data from: {data_path}")
    data = pd.read_csv(data_path)
    data.columns = data.columns.str.strip().str.lower()
    data = data.drop(columns=[col for col in data.columns if 'unnamed' in col.lower()])
    data = data.rename(columns={'open': 'Open', 'high': 'High', 'low': 'Low', 'close': 'Close', 'volume': 'Volume'})
    data = data.set_index(pd.to_datetime(data['datetime']))
    print(f"🌙 Data loaded: {len(data)} rows, columns: {list(data.columns)}")

    bt = Backtest(data, KalmanSentiment, cash=1_000_000, commission=0.002)
    stats = bt.run()

    # 🌙 CRITICAL: Print full stats for Moon Dev's parser!
    print("\n" + "="*80)
    print("📊 BACKTEST STATISTICS (Moon Dev's Format)")
    print("="*80)
    print(stats)
    print("="*80 + "\n")

    # THEN: Run multi-data testing
    # 🌙 Moon Dev: EXTERNAL DEPENDENCY - Requires moon-dev-trading-bots repo
    # Clone from: https://github.com/moondevonyt/moon-dev-trading-bots
    # Expected location: ../moon-dev-trading-bots (sibling to this repo)
    external_backtests = str(project_root.parent / 'moon-dev-trading-bots' / 'backtests')
    sys.path.append(external_backtests)
    from multi_data_tester import test_on_all_data

    print("\n" + "="*80)
    print("🚀 MOON DEV'S MULTI-DATA BACKTEST - Testing on 25+ Data Sources!")
    print("="*80)

    # Test this strategy on all configured data sources
    # This will test on: BTC, ETH, SOL (multiple timeframes), AAPL, TSLA, ES, NQ, GOOG, NVDA
    # IMPORTANT: verbose=False to prevent plotting (causes timeouts in parallel processing!)
    results = test_on_all_data(KalmanSentiment, 'KalmanSentiment', verbose=False)

    if results is not None:
        print("\n✅ Multi-data testing complete! Results saved in ./results/ folder")
        print(f"📊 Tested on {len(results)} different data sources")
    else:
        print("\n⚠️ No results generated - check for errors above")