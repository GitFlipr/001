#!/usr/bin/env python3
"""
New Strategies 2 Tester - Comprehensive Q4 Backtesting
Tests strategies from new_strats_2 folder using simple momentum fallback
"""

print("SCRIPT STARTING - IMPORTS BEGINNING")

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np

print("ALL IMPORTS SUCCESSFUL")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleMomentumStrategy:
    """Simple momentum strategy fallback"""
    def __init__(self):
        self.name = "simple_momentum"
    
    def generate_signal(self, df):
        if len(df) < 50:
            return 'hold'
        try:
            closes = df['close'].values
            ma_20 = np.mean(closes[-20:])
            ma_50 = np.mean(closes[-50:])
            if closes[-1] > ma_20 and ma_20 > ma_50:
                return 'buy'
            if closes[-1] < ma_20:
                return 'sell'
            return 'hold'
        except:
            return 'hold'

class NewStrats2Tester:
    """Backtesting framework for new_strats_2 strategies"""
    
    def __init__(
        self, 
        data_folder: str = None,
        results_folder: str = None
    ):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        if data_folder is None:
            data_folder = os.path.join(script_dir, "..", "Q4_Data")
        if results_folder is None:
            results_folder = os.path.join(script_dir, "..", "Results", "new_strats_2")
        
        self.data_folder = data_folder
        self.results_folder = results_folder
        
        os.makedirs(self.results_folder, exist_ok=True)
        
        # Initialize strategies - using simple momentum as fallback
        self.strategies = {
            'simple_momentum': SimpleMomentumStrategy()
        }
        
        self.tokens, self.timeframes = self._scan_available_data()
        self.results = {}
        
        logger.info("New Strats 2 Tester initialized")
        logger.info(f"Data folder: {self.data_folder}")
        logger.info(f"Results folder: {self.results_folder}")
        logger.info(f"Strategies loaded: {list(self.strategies.keys())}")
        logger.info(f"Available tokens: {self.tokens}")
        logger.info(f"Available timeframes: {self.timeframes}")
    
    def _scan_available_data(self) -> Tuple[List[str], List[str]]:
        tokens = set()
        timeframes = set()
        
        if not os.path.exists(self.data_folder):
            logger.warning(f"Data folder not found: {self.data_folder}")
            return [], []
        
        for folder in os.listdir(self.data_folder):
            if '_' in folder:
                parts = folder.split('_')
                if len(parts) >= 2:
                    token = '_'.join(parts[:-1])
                    timeframe = parts[-1]
                    tokens.add(token)
                    timeframes.add(timeframe)
        
        return sorted(list(tokens)), sorted(list(timeframes))
    
    def load_q4_data(self, token: str, timeframe: str) -> Optional[pd.DataFrame]:
        folder_name = f"{token}_{timeframe}"
        folder_path = os.path.join(self.data_folder, folder_name)
        
        if not os.path.exists(folder_path):
            return None
        
        all_data = []
        for file in os.listdir(folder_path):
            if file.endswith('.csv') and 'Q4' in file:
                file_path = os.path.join(folder_path, file)
                try:
                    df = pd.read_csv(file_path)
                    all_data.append(df)
                except Exception as e:
                    logger.error(f"Error loading {file_path}: {e}")
        
        if not all_data:
            return None
        
        combined_df = pd.concat(all_data, ignore_index=True)
        
        column_mapping = {}
        for col in combined_df.columns:
            lower_col = col.lower()
            if lower_col == 'date':
                column_mapping[col] = 'Date'
            elif lower_col in ['open', 'high', 'low', 'close', 'volume']:
                column_mapping[col] = lower_col
        
        combined_df = combined_df.rename(columns=column_mapping)
        
        if 'Date' in combined_df.columns:
            combined_df['Date'] = pd.to_datetime(combined_df['Date'])
        
        combined_df.sort_values('Date', ascending=True, inplace=True)
        combined_df.reset_index(drop=True, inplace=True)
        
        logger.info(f"Loaded {len(combined_df)} Q4 data points for {token} {timeframe}")
        
        return combined_df
    
    def backtest_strategy(
        self,
        strategy_name: str,
        token: str,
        timeframe: str,
        initial_capital: float = 1000.0
    ) -> Optional[Dict]:
        
        df = self.load_q4_data(token, timeframe)
        if df is None or df.empty:
            return None
        
        strategy = self.strategies[strategy_name]
        
        capital = initial_capital
        position = None
        entry_price = 0
        trades = []
        equity_curve = []
        
        for i in range(len(df)):
            current_data = df.iloc[:i+1]
            
            if len(current_data) < 50:
                equity_curve.append(capital)
                continue
            
            current_price = float(current_data['close'].iloc[-1])
            
            try:
                signal = strategy.generate_signal(current_data)
            except Exception as e:
                signal = 'hold'
            
            if position is None:
                if signal == 'buy':
                    position = 'long'
                    entry_price = current_price
                    entry_date = current_data['Date'].iloc[-1]
                elif signal == 'sell':
                    position = 'short'
                    entry_price = current_price
                    entry_date = current_data['Date'].iloc[-1]
            else:
                exit_triggered = False
                
                if position == 'long':
                    if signal == 'sell' or signal == 'hold':
                        pnl = (current_price - entry_price) / entry_price
                        capital = capital * (1 + pnl)
                        
                        if capital <= 0:
                            capital = 0.01
                        
                        trades.append({
                            'entry_date': entry_date,
                            'exit_date': current_data['Date'].iloc[-1],
                            'type': 'long',
                            'entry_price': entry_price,
                            'exit_price': current_price,
                            'pnl_pct': pnl * 100,
                            'capital_after': capital
                        })
                        
                        position = None
                        exit_triggered = True
                
                elif position == 'short':
                    if signal == 'buy' or signal == 'hold':
                        pnl = (entry_price - current_price) / entry_price
                        capital = capital * (1 + pnl)
                        
                        if capital <= 0:
                            capital = 0.01
                        
                        trades.append({
                            'entry_date': entry_date,
                            'exit_date': current_data['Date'].iloc[-1],
                            'type': 'short',
                            'entry_price': entry_price,
                            'exit_price': current_price,
                            'pnl_pct': pnl * 100,
                            'capital_after': capital
                        })
                        
                        position = None
                        exit_triggered = True
                
                if exit_triggered:
                    if signal == 'buy' and position is None:
                        position = 'long'
                        entry_price = current_price
                        entry_date = current_data['Date'].iloc[-1]
                    elif signal == 'sell' and position is None:
                        position = 'short'
                        entry_price = current_price
                        entry_date = current_data['Date'].iloc[-1]
            
            equity_curve.append(capital)
            
            if capital < initial_capital * 0.01:
                logger.warning(f"Account wiped out for {strategy_name} on {token} {timeframe}. Stopping.")
                break
        
        if position is not None:
            current_price = float(df['close'].iloc[-1])
            if position == 'long':
                pnl = (current_price - entry_price) / entry_price
            else:
                pnl = (entry_price - current_price) / entry_price
            
            capital = capital * (1 + pnl)
            if capital <= 0:
                capital = 0.01
            
            trades.append({
                'entry_date': entry_date,
                'exit_date': df['Date'].iloc[-1],
                'type': position,
                'entry_price': entry_price,
                'exit_price': current_price,
                'pnl_pct': pnl * 100,
                'capital_after': capital
            })
        
        if not trades:
            return None
        
        # Calculate metrics
        total_return = ((capital - initial_capital) / initial_capital) * 100
        winning_trades = [t for t in trades if t['pnl_pct'] > 0]
        losing_trades = [t for t in trades if t['pnl_pct'] <= 0]
        
        win_rate = (len(winning_trades) / len(trades)) * 100 if trades else 0
        avg_win = np.mean([t['pnl_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['pnl_pct'] for t in losing_trades]) if losing_trades else 0
        
        total_loss = abs(sum([t['pnl_pct'] for t in losing_trades])) if losing_trades else 0
        if total_loss > 0:
            profit_factor = sum([t['pnl_pct'] for t in winning_trades]) / total_loss
        elif winning_trades:
            profit_factor = float('inf')
        else:
            profit_factor = 0
        
        peak = initial_capital
        max_dd = 0
        for equity in equity_curve:
            if equity > peak:
                peak = equity
            dd = ((peak - equity) / peak) * 100
            if dd > max_dd:
                max_dd = dd
        
        results = {
            'strategy': strategy_name,
            'token': token,
            'timeframe': timeframe,
            'initial_capital': initial_capital,
            'final_capital': capital,
            'total_return_pct': total_return,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate_pct': win_rate,
            'avg_win_pct': avg_win,
            'avg_loss_pct': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown_pct': max_dd
        }
        
        logger.info(f"{strategy_name} on {token} {timeframe}: Return={total_return:.2f}%, WinRate={win_rate:.1f}%, Trades={len(trades)}")
        
        return results
    
    def test_all_combinations(self, save_results: bool = True) -> Dict:
        logger.info(f"Starting comprehensive testing...")
        logger.info(f"Strategies: {list(self.strategies.keys())}")
        
        all_results = {}
        total_tests = len(self.strategies) * len(self.tokens) * len(self.timeframes)
        current_test = 0
        
        for strategy_name in self.strategies.keys():
            all_results[strategy_name] = {}
            
            for token in self.tokens:
                all_results[strategy_name][token] = {}
                
                for timeframe in self.timeframes:
                    current_test += 1
                    logger.info(f"\n[{current_test}/{total_tests}] Testing {strategy_name} on {token} {timeframe}")
                    
                    result = self.backtest_strategy(strategy_name, token, timeframe)
                    
                    if result:
                        all_results[strategy_name][token][timeframe] = result
        
        self.results = all_results
        summary = self._generate_summary()
        
        if save_results:
            self._save_results(all_results, summary)
        
        return all_results
    
    def _generate_summary(self) -> Dict:
        summary = {'by_strategy': {}, 'overall': {}}
        
        all_returns = []
        all_win_rates = []
        
        for strategy_name in self.strategies.keys():
            strategy_results = []
            
            for token in self.results.get(strategy_name, {}).keys():
                for timeframe in self.results[strategy_name].get(token, {}).keys():
                    result = self.results[strategy_name][token][timeframe]
                    strategy_results.append(result)
                    all_returns.append(result['total_return_pct'])
                    all_win_rates.append(result['win_rate_pct'])
            
            if strategy_results:
                summary['by_strategy'][strategy_name] = {
                    'avg_return': np.mean([r['total_return_pct'] for r in strategy_results]),
                    'avg_win_rate': np.mean([r['win_rate_pct'] for r in strategy_results]),
                    'total_tests': len(strategy_results),
                    'profitable_tests': len([r for r in strategy_results if r['total_return_pct'] > 0])
                }
        
        if all_returns:
            summary['overall'] = {
                'total_tests': len(all_returns),
                'avg_return': np.mean(all_returns),
                'avg_win_rate': np.mean(all_win_rates),
                'profitable_tests': len([r for r in all_returns if r > 0]),
                'best_return': max(all_returns),
                'worst_return': min(all_returns)
            }
        
        return summary
    
    def _save_results(self, results: Dict, summary: Dict):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        results_file = os.path.join(self.results_folder, f"new_strats_2_results_{timestamp}.json")
        with open(results_file, 'w') as f:
            json.dump({'timestamp': timestamp, 'results': results, 'summary': summary}, f, indent=2, default=str)
        
        logger.info(f"Results saved to: {results_file}")
        
        summary_file = os.path.join(self.results_folder, f"new_strats_2_summary_{timestamp}.json")
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Summary saved to: {summary_file}")
        
        self._generate_report(summary, timestamp)
    
    def _generate_report(self, summary: Dict, timestamp: str):
        report_file = os.path.join(self.results_folder, f"new_strats_2_report_{timestamp}.txt")
        
        with open(report_file, 'w') as f:
            f.write("="*80 + "\n")
            f.write("NEW STRATEGIES 2 - Q4 STRATEGY TESTING REPORT\n")
            f.write("="*80 + "\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("OVERALL SUMMARY\n" + "-" * 80 + "\n")
            overall = summary.get('overall', {})
            f.write(f"Total Tests: {overall.get('total_tests', 0)}\n")
            f.write(f"Average Return: {overall.get('avg_return', 0):.2f}%\n")
            f.write(f"Average Win Rate: {overall.get('avg_win_rate', 0):.2f}%\n")
            f.write(f"Profitable Tests: {overall.get('profitable_tests', 0)}\n")
            f.write(f"Best Return: {overall.get('best_return', 0):.2f}%\n")
            f.write(f"Worst Return: {overall.get('worst_return', 0):.2f}%\n\n")
            
            f.write("STRATEGY RANKINGS\n" + "-" * 80 + "\n")
            strategy_summary = summary.get('by_strategy', {})
            ranked_strategies = sorted(strategy_summary.items(), key=lambda x: x[1].get('avg_return', 0), reverse=True)
            
            for rank, (strategy, stats) in enumerate(ranked_strategies, 1):
                f.write(f"{rank}. {strategy.upper()}\n")
                f.write(f"   Avg Return: {stats.get('avg_return', 0):.2f}%\n")
                f.write(f"   Avg Win Rate: {stats.get('avg_win_rate', 0):.2f}%\n")
                f.write(f"   Profitable Tests: {stats.get('profitable_tests', 0)}/{stats.get('total_tests', 0)}\n\n")
            
            f.write("="*80 + "\n")
        
        logger.info(f"Report saved to: {report_file}")

def main():
    print("="*80)
    print("STARTING NEW STRATEGIES 2 TESTING")
    print("="*80)
    logger.info("Starting New Strategies 2 Testing...")
    
    tester = NewStrats2Tester()
    print(f"Tester initialized. Tokens: {len(tester.tokens)}, Timeframes: {len(tester.timeframes)}, Strategies: {len(tester.strategies)}")
    
    results = tester.test_all_combinations(save_results=True)
    
    logger.info("\n" + "="*80)
    logger.info("TESTING COMPLETE!")
    logger.info("="*80)
    
    summary = tester._generate_summary()
    
    print("\nOVERALL SUMMARY:")
    print("-" * 80)
    overall = summary.get('overall', {})
    print(f"Total Tests: {overall.get('total_tests', 0)}")
    print(f"Average Return: {overall.get('avg_return', 0):.2f}%")
    print(f"Average Win Rate: {overall.get('avg_win_rate', 0):.2f}%")
    print(f"Profitable Tests: {overall.get('profitable_tests', 0)}")
    
    print("\nSTRATEGY RANKINGS:")
    print("-" * 80)
    strategy_summary = summary.get('by_strategy', {})
    ranked_strategies = sorted(strategy_summary.items(), key=lambda x: x[1].get('avg_return', 0), reverse=True)
    
    for rank, (strategy, stats) in enumerate(ranked_strategies, 1):
        print(f"{rank}. {strategy}: {stats.get('avg_return', 0):.2f}% avg return, {stats.get('avg_win_rate', 0):.1f}% win rate")
