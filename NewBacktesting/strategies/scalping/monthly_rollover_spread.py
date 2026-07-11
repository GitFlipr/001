import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def calculate_calendar_spread(data):
  """Calculates the calendar spread between front-month and next-month futures contracts.

  Args:
    data: A pandas DataFrame containing the futures prices.

  Returns:
    A pandas Series containing the calendar spread.
  """

  front_month = data.iloc[:, 0]
  next_month = data.iloc[:, 1]
  calendar_spread = next_month - front_month
  return calendar_spread

def enter_long_calendar_spread(data, entry_threshold):
  """Enters a long calendar spread if the spread is above the entry threshold.

  Args:
    data: A pandas DataFrame containing the futures prices.
    entry_threshold: The entry threshold for the long calendar spread.

  Returns:
    A pandas Series containing the long calendar spread positions.
  """

  calendar_spread = calculate_calendar_spread(data)
  long_positions = np.where(calendar_spread > entry_threshold, 1, 0)
  return long_positions

def enter_short_calendar_spread(data, entry_threshold):
  """Enters a short calendar spread if the spread is below the entry threshold.

  Args:
    data: A pandas DataFrame containing the futures prices.
    entry_threshold: The entry threshold for the short calendar spread.

  Returns:
    A pandas Series containing the short calendar spread positions.
  """

  calendar_spread = calculate_calendar_spread(data)
  short_positions = np.where(calendar_spread < -entry_threshold, -1, 0)
  return short_positions

def exit_positions(data, exit_threshold):
  """Exits all positions if the spread reaches the exit threshold.

  Args:
    data: A pandas DataFrame containing the futures prices.
    exit_threshold: The exit threshold for the calendar spread.

  Returns:
    A pandas Series containing the exit positions.
  """

  calendar_spread = calculate_calendar_spread(data)
  exit_positions = np.where(abs(calendar_spread) >= exit_threshold, 0, 1)
  return exit_positions

def backtest_calendar_spread(data, entry_threshold, exit_threshold):
  """Backtests a calendar spread strategy.

  Args:
    data: A pandas DataFrame containing the futures prices.
    entry_threshold: The entry threshold for the calendar spread.
    exit_threshold: The exit threshold for the calendar spread.

  Returns:
    A pandas DataFrame containing the backtest results.
  """

  long_positions = enter_long_calendar_spread(data, entry_threshold)
  short_positions = enter_short_calendar_spread(data, entry_threshold)
  exit_positions = exit_positions(data, exit_threshold)
  positions = long_positions + short_positions
  positions = positions * exit_positions
  returns = positions * calculate_calendar_spread(data)
  cumulative_returns = (1 + returns).cumprod() - 1
  return cumulative_returns

# Example usage:
data = pd.read_csv('futures_data.csv')
entry_threshold = 0.05
exit_threshold = 0.1
cumulative_returns = backtest_calendar_spread(data, entry_threshold, exit_threshold)
plt.plot(cumulative_returns)
plt.show()