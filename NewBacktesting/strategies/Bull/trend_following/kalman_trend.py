"""Kalman filter on close for trend. From set_2/052."""
import numpy as np
from backtesting import Strategy


def _kalman_1d(close: np.ndarray, q: float = 1e-5, r: float = 1e-2) -> np.ndarray:
    close = np.asarray(close, dtype=float)
    n = len(close)
    x, p = np.zeros(n), np.zeros(n)
    x[0], p[0] = close[0], 1.0
    for i in range(1, n):
        p_pred = p[i - 1] + q
        k = p_pred / (p_pred + r)
        x[i] = x[i - 1] + k * (close[i] - x[i - 1])
        p[i] = (1 - k) * p_pred
    return x


class KalmanTrend(Strategy):
    q = 1e-5
    r = 1e-2

    def init(self):
        self.kf = self.I(
            lambda c: _kalman_1d(np.asarray(c, dtype=float), self.q, self.r),
            self.data.Close,
        )

    def next(self):
        if len(self.data) < 5:
            return
        if np.isnan(self.kf[-1]):
            return
        slope = self.kf[-1] - self.kf[-2]
        c = self.data.Close[-1]
        if not self.position:
            if slope > 0 and c > self.kf[-1]:
                self.buy()
            elif slope < 0 and c < self.kf[-1]:
                self.sell()
        else:
            if self.position.is_long and c < self.kf[-1]:
                self.position.close()
            elif self.position.is_short and c > self.kf[-1]:
                self.position.close()
