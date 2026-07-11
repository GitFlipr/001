import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtest_utils import run_all_timeframes
import logging
import os
import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ADX_Fib_Scalping(Strategy):
    # Strategy parameters
    adx_period = 14
    adx_threshold = 25  # Minimum ADX value for trend strength
    risk_per_trade = 0.01  # 1% risk per trade
    stop_loss_pct = 0.005  # 0.5% stop loss for scalping
    take_profit_pct = 0.01 # 1% take profit for scalping
    min_volume = 50        # Minimum volume requirement
    min_volatility = 0.00005 # Minimum volatility requirement
    fib_levels = [0.236, 0.382, 0.5, 0.618, 0.786]  # Fibonacci levels

    def init(self):
        # Initialize ADX
        def adx(high, low, close, period):
            tr1 = pd.Series(high - low)
            tr2 = pd.Series(abs(high - close.shift(1)))
            tr3 = pd.Series(abs(low - close.shift(1)))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(period).mean()
            
            up_move = high - high.shift(1)
            down_move = low.shift(1) - low
            
            plus_dm = pd.Series(np.where((up_move > down_move) & (up_move > 0), up_move, 0), index=high.index)
            minus_dm = pd.Series(np.where((down_move > up_move) & (down_move > 0), down_move, 0), index=high.index)
            
            plus_di = 100 * plus_dm.rolling(period).mean() / atr
            minus_di = 100 * minus_dm.rolling(period).mean() / atr
            
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(period).mean()
            
            return adx, plus_di, minus_di

        self.adx, self.plus_di, self.minus_di = self.I(adx, self.data.High, 
                                                      self.data.Low, 
                                                      self.data.Close, 
                                                      self.adx_period)
        
        # Calculate volatility (ATR-like)
        self.volatility = self.I(lambda x: pd.Series(x).rolling(window=14).std(), self.data.Close)
        
        # Track positions
        self.position_size = 0
        self.entry_price = 0
        self.stop_loss = 0
        self.take_profit = 0

    def calculate_position_size(self, price, stop_loss):
        """Calculate position size based on risk management"""
        risk_amount = self.equity * self.risk_per_trade
        risk_per_unit = abs(price - stop_loss)
        if risk_per_unit == 0:
            return 0
        
        # Calculate raw position size
        raw_size = risk_amount / risk_per_unit
        
        # Convert to a fraction of equity (between 0 and 1)
        position_size = raw_size * price / self.equity
        
        # Ensure position size is between 0 and 1
        position_size = min(max(position_size, 0), 1)
        
        return position_size

    def calculate_fib_levels(self, high, low):
        """Calculate Fibonacci levels for the given high and low"""
        diff = high - low
        levels = {}
        for fib in self.fib_levels:
            levels[fib] = high - (diff * fib)
        return levels

    def next(self):
        # Get current values
        price = self.data.Close[-1]
        volume = self.data.Volume[-1]
        volatility = self.volatility[-1]

        # Calculate Fibonacci levels for the last 20 candles
        high = max(self.data.High[-20:])
        low = min(self.data.Low[-20:])
        fib_levels = self.calculate_fib_levels(high, low)

        # Check if we have an open position
        if self.position.is_long:
            # Check take profit
            if price >= self.take_profit:
                logger.info(f"Take profit hit at {price:.2f}")
                self.position.close()
                self.position_size = 0
            # Check stop loss
            elif price <= self.stop_loss:
                logger.info(f"Stop loss hit at {price:.2f}")
                self.position.close()
                self.position_size = 0
            # Check exit conditions
            elif (self.plus_di[-1] < self.minus_di[-1] and 
                  price < fib_levels[0.5]):
                logger.info(f"Exit long position at {price:.2f}")
                self.position.close()
                self.position_size = 0

        elif self.position.is_short:
            # Check take profit
            if price <= self.take_profit:
                logger.info(f"Take profit hit at {price:.2f}")
                self.position.close()
                self.position_size = 0
            # Check stop loss
            elif price >= self.stop_loss:
                logger.info(f"Stop loss hit at {price:.2f}")
                self.position.close()
                self.position_size = 0
            # Check exit conditions
            elif (self.plus_di[-1] > self.minus_di[-1] and 
                  price > fib_levels[0.5]):
                logger.info(f"Exit short position at {price:.2f}")
                self.position.close()
                self.position_size = 0

        # Entry conditions
        else:
            # Long entry conditions
            if (self.adx[-1] > self.adx_threshold and
                self.plus_di[-1] > self.minus_di[-1] and 
                price > fib_levels[0.5] and
                volume > self.min_volume and 
                volatility > self.min_volatility):
                
                self.stop_loss = price * (1 - self.stop_loss_pct)
                self.take_profit = price * (1 + self.take_profit_pct)
                self.position_size = self.calculate_position_size(price, self.stop_loss)
                
                if self.position_size > 0:
                    logger.info(f"Long entry at {price:.2f}, Stop: {self.stop_loss:.2f}, Target: {self.take_profit:.2f}, Size: {self.position_size:.4f}")
                    self.buy(size=self.position_size)

            # Short entry conditions
            elif (self.adx[-1] > self.adx_threshold and
                  self.plus_di[-1] < self.minus_di[-1] and 
                  price < fib_levels[0.5] and
                  volume > self.min_volume and 
                  volatility > self.min_volatility):
                
                self.stop_loss = price * (1 + self.stop_loss_pct)
                self.take_profit = price * (1 - self.take_profit_pct)
                self.position_size = self.calculate_position_size(price, self.stop_loss)
                
                if self.position_size > 0:
                    logger.info(f"Short entry at {price:.2f}, Stop: {self.stop_loss:.2f}, Target: {self.take_profit:.2f}, Size: {self.position_size:.4f}")
                    self.sell(size=self.position_size)

def find_available_data():
    """Find all available data files across all timeframe folders"""
    project_root = os.getcwd()
    base_path = os.path.join(project_root, 'backtesting', 'data')
    timeframes = ['1m', '5m', '15m', '30m', '1h', '4h', '1d']
    available_data = {}
    
    for tf in timeframes:
        tf_path = os.path.join(base_path, tf)
        if os.path.exists(tf_path):
            # Find all CSV files in the timeframe folder
            csv_files = glob.glob(os.path.join(tf_path, '*.csv'))
            if csv_files:
                available_data[tf] = []
                for file in csv_files:
                    # Extract token name from filename
                    token = os.path.basename(file).split('_')[0]
                    if token not in available_data[tf]:
                        available_data[tf].append(token)
    
    return available_data

if __name__ == "__main__":
    # Find all available data
    available_data = find_available_data()
    
    # Run backtests for all available data
    for timeframe, tokens in available_data.items():
        for token in tokens:
            logger.info(f"Running adx_fib_scalping backtest for {token} on {timeframe} timeframe...")
            run_all_timeframes(
                strategy_class=ADX_Fib_Scalping,
                strategy_name='adx_fib_scalping',
                symbols=[token],
                timeframes=[timeframe],
                start_date=None,  # No date restrictions
                end_date=None     # No date restrictions
            )
