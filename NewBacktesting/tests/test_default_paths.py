import unittest
from pathlib import Path

from backtest.config import get_default_data_dir, get_default_results_dir, get_default_strategies_dir


class DefaultPathConfigurationTest(unittest.TestCase):
    def test_default_paths_use_project_locations(self):
        base = Path(__file__).resolve().parents[1]

        self.assertEqual(get_default_data_dir(), base / "data" / "Hyperliquid")
        self.assertEqual(get_default_strategies_dir(), base / "strategies")
        self.assertEqual(get_default_results_dir(), Path(r"D:\Results"))


if __name__ == "__main__":
    unittest.main()
