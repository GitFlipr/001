import unittest
from pathlib import Path

from backtest.batch_runner import BatchBacktestRunner


class BatchBacktestRunnerTest(unittest.TestCase):
    def test_runner_discovers_files_and_strategies(self):
        runner = BatchBacktestRunner(
            data_dir=Path(__file__).resolve().parents[1] / "data" / "Hyperliquid",
            strategies_dir=Path(__file__).resolve().parents[1] / "strategies",
            results_dir=Path(__file__).resolve().parents[1] / "results" / "test_run",
            max_workers=2,
            recursive=True,
        )
        data_files = runner.discover_data_files("*.csv")
        strategies = runner.discover_strategies(max_strategies=3)
        self.assertIsInstance(data_files, list)
        self.assertIsInstance(strategies, list)


if __name__ == "__main__":
    unittest.main()
