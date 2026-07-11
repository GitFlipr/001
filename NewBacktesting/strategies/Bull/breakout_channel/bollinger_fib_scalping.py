import pandas_ta as ta
import pandas as pd

def bollinger_fib_scalping(df):
    # Calculate Bollinger Bands
    bb = ta.bbands(df['close'], length=20, std=2)
    df = df.join(bb)
    # Calculate EMA
    df['ema20'] = ta.ema(df['close'], length=20)
    
    # Mock Fibonacci levels
    swing_high = df['high'].max()
    swing_low = df['low'].min()
    fib_50 = swing_high - (swing_high - swing_low) * 0.5
    fib_618 = swing_high - (swing_high - swing_low) * 0.618
    
    # Signals
    df['signal'] = 0
    for i in range(1, len(df)):
        if (df['close'].iloc[i] <= df['BBL_20_2.0'].iloc[i] and 
            df['close'].iloc[i] <= fib_50 and df['close'].iloc[i] > df['ema20'].iloc[i]):
            df['signal'].iloc[i] = 1  # Buy
        elif df['close'].iloc[i] >= df['BBM_20_2.0'].iloc[i]:
            df['signal'].iloc[i] = -1  # Sell
    
    return df