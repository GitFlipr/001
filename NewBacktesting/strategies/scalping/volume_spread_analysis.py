import pandas as pd
import numpy as np
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import logging
import os
import glob

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SMA_ADX_Bollinger_Strategy(Strategy):
    # Strategy parameters
    sma_period = 20
    adx_period = 14
    bb_period = 20
    bb_std = 2
    adx_threshold = 25
    risk_per_trade = 0.01  # 1% risk per trade
    stop_loss_pct = 0.01   # 1% stop loss
    take_profit_pct = 0.02 # 2% take profit
    min_volume = 50        # Minimum volume requirement
    min_volatility = 0.00005 # Minimum volatility requirement

    @staticmethod
    def _rolling_mean(arr, window):
        return pd.Series(arr).rolling(window).mean().to_numpy()

    @staticmethod
    def _rolling_std(arr, window):
        return pd.Series(arr).rolling(window=window).std().to_numpy()

    def init(self):
        # Initialize indicators
        # SMA
        self.sma = self.I(self._rolling_mean, self.data.Close, self.sma_period)
        
        # ADX
        def adx(high, low, close, period):
            tr1 = pd.Series(high - low)
            tr2 = pd.Series(abs(high - close.shift(1)))
            tr3 = pd.Series(abs(low - close.shift(1)))
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(period).mean()
            
            up_move = high - high.shift(1)
            down_move = low.shift(1) - low
            
            plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
            minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
            
            plus_di = 100 * pd.Series(plus_dm).rolling(period).mean() / atr
            minus_di = 100 * pd.Series(minus_dm).rolling(period).mean() / atr
            
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            return dx.rolling(period).mean()
        
        self.adx = self.I(adx, self.data.High, self.data.Low, self.data.Close, self.adx_period)
        
        # Bollinger Bands
        def bollinger_bands(close, period, std):
            sma = pd.Series(close).rolling(period).mean()
            std_dev = pd.Series(close).rolling(period).std()
            upper_band = sma + (std_dev * std)
            lower_band = sma - (std_dev * std)
            return upper_band, lower_band
        
        self.bb_upper, self.bb_lower = self.I(bollinger_bands, self.data.Close, self.bb_period, self.bb_std)
        
        # Calculate volatility (ATR-like)
        self.volatility = self.I(self._rolling_std, self.data.Close, 14)
        
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

    def next(self):
        # Get current values
        price = self.data.Close[-1]
        volume = self.data.Volume[-1]
        volatility = self.volatility[-1]

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
            elif (price < self.sma[-1] or 
                  self.adx[-1] < self.adx_threshold or
                  price >= self.bb_upper[-1]):
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
            elif (price > self.sma[-1] or 
                  self.adx[-1] < self.adx_threshold or
                  price <= self.bb_lower[-1]):
                logger.info(f"Exit short position at {price:.2f}")
                self.position.close()
                self.position_size = 0

        # Entry conditions
        else:
            # Long entry conditions
            if (price > self.sma[-1] and 
                self.adx[-1] > self.adx_threshold and
                price < self.bb_upper[-1] and
                volume > self.min_volume and 
                volatility > self.min_volatility):
                
                self.stop_loss = price * (1 - self.stop_loss_pct)
                self.take_profit = price * (1 + self.take_profit_pct)
                self.position_size = self.calculate_position_size(price, self.stop_loss)
                
                if self.position_size > 0:
                    logger.info(f"Long entry at {price:.2f}, Stop: {self.stop_loss:.2f}, Target: {self.take_profit:.2f}, Size: {self.position_size:.4f}")
                    self.buy(size=self.position_size)

            # Short entry conditions
            elif (price < self.sma[-1] and 
                  self.adx[-1] > self.adx_threshold and
                  price > self.bb_lower[-1] and
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
    base_path = os.path.join('backtesting', 'data')
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
