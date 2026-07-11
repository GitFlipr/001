# trading_strategies.py

import numpy as np
import pandas as pd
from pykalman import KalmanFilter
from hmmlearn import hmm

class KalmanFilterStrategy:
    def __init__(self, initial_state_mean, initial_state_covariance):
        self.kf = KalmanFilter(initial_state_mean=initial_state_mean,
                                initial_state_covariance=initial_state_covariance)

    def apply_filter(self, observed_data):
        # Apply the Kalman Filter to the observed data
        self.kf = self.kf.em(observed_data, n_iter=10)
        (filtered_state_means, filtered_state_covariances) = self.kf.filter(observed_data)
        return filtered_state_means

class HiddenMarkovModelStrategy:
    def __init__(self, n_components):
        self.model = hmm.GaussianHMM(n_components=n_components)

    def fit_model(self, observed_data):
        # Fit the HMM model to the observed data
        self.model.fit(observed_data)
    
    def predict(self, n_steps):
        # Predict future states using the fitted HMM model
        return self.model.sample(n_steps)
