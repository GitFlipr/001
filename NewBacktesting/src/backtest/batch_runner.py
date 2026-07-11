from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type

import pandas as pd

# ---------------------------------------------------------------
# sys.path bootstrap — MUST happen before any backtest.* imports
# Resolves from this file's location so it works regardless of
# cwd, PYTHONPATH, or how the script was launched.
# ---------------------------------------------------------------
_THIS_FILE   = Path(__file__).resolve()
_SRC_ROOT    = _THIS_FILE.parents[1]   # src/backtest/batch_runner.py → src/
_PROJECT_ROOT = _SRC_ROOT.parent        # src/ → NewBacktesting/

for _p in (_SRC_ROOT, _PROJECT_ROOT):
    _ps = str(_p)
    if _ps not in sys.path:
        sys.path.insert(0, _ps)

# Invalidate any stale "strategies" import cache entries that may
# have been cached before the path was set correctly.
for _key in list(sys.modules.keys()):
    if _key == "strategies" or _key.startswith("strategies."):
        del sys.modules[_key]

from backtest.config import get_default_data_dir, get_default_results_dir, get_default_strategies_dir
from backtest.core.backtest import Backtest
from backtest.data.loader import DataLoader
from backtest.strategies.base import Strategy
from backtest.strategies.discovery import StrategyDiscovery


class BatchBacktestRunner:
    def __init__(
        self,
        data_dir: Optional[Path] = None,
        strategies_dir: Optional[Path] = None,
        results_dir: Optional[Path] = None,
        max_workers: int = 4,
        recursive: bool = True,
    ):
        self.data_dir = Path(data_dir or get_default_data_dir())
        self.strategies_dir = Path(strategies_dir or get_default_strategies_dir())
        self.results_dir = Path(results_dir or get_default_results_dir())
        self.max_workers = max_workers
        self.recursive = recursive

    def discover_data_files(self, pattern: str = "*.csv") -> List[Path]:
        if self.recursive:
            return sorted(self.data_dir.rglob(pattern))
        return sorted(self.data_dir.glob(pattern))

    def discover_strategies(self, max_strategies: Optional[int] = None) -> List[Tuple[str, Type[Strategy]]]:
        # Guarantee project root is on sys.path regardless of how runner was invoked
        strategies_parent = str(self.strategies_dir.parent.resolve())
        if strategies_parent not in sys.path:
            sys.path.insert(0, strategies_parent)
            # Clear stale cache entries so the fresh path is honoured
            for key in list(sys.modules.keys()):
                if key == "strategies" or key.startswith("strategies."):
                    del sys.modules[key]

        print(f"[BatchRunner] sys.path[0:2]     : {sys.path[:2]}")
        print(f"[BatchRunner] strategies_dir    : {self.strategies_dir}")

        discovery = StrategyDiscovery(discovery_root=self.strategies_dir)
        return discovery.discover_strategies(max_strategies=max_strategies)

    def _load_frame(self, file_path: Path) -> pd.DataFrame:
        return DataLoader.from_csv(file_path)

    def _run_single_job(self, job: Dict[str, Any]) -> Dict[str, Any]:
        file_path = Path(job["file_path"])
        strategy_name = job["strategy_name"]
        strategy_cls = job["strategy_cls"]
        params = job.get("params", {})

        try:
            frame = self._load_frame(file_path)
            backtest = Backtest(frame, strategy_cls)
            results = backtest.run(params=params)
            output_file = backtest.save_results(output_dir=self.results_dir / strategy_name, filename=f"{file_path.stem}.parquet")
            return {
                "status": "ok",
                "file": str(file_path),
                "strategy": strategy_name,
                "output": str(output_file),
                "metrics": results.get("metrics", {}),
            }
        except Exception as exc:  # noqa: BLE001
            return {
                "status": "error",
                "file": str(file_path),
                "strategy": strategy_name,
                "error": str(exc),
            }

    def run(
        self,
        strategy_packages: Optional[Sequence[str]] = None,
        max_strategies: Optional[int] = None,
        data_pattern: str = "*.csv",
        params: Optional[Dict[str, Any]] = None,
        parallel: bool = True,
    ) -> List[Dict[str, Any]]:
        self.results_dir.mkdir(parents=True, exist_ok=True)
        data_files = self.discover_data_files(data_pattern)
        strategies = self.discover_strategies(max_strategies=max_strategies)

        print(f"[BatchRunner] Data files found  : {len(data_files)}")
        print(f"[BatchRunner] Strategies found  : {len(strategies)}")
        if strategies:
            print(f"[BatchRunner] First 5 strategies: {[n for n,_ in strategies[:5]]}")

        if not data_files:
            print(f"[BatchRunner] WARNING: No data files matched '{data_pattern}' in {self.data_dir}")
            return []
        if not strategies:
            print(f"[BatchRunner] WARNING: No Strategy subclasses found under {self.strategies_dir}")
            return []

        jobs = []
        for data_file in data_files:
            for strategy_name, strategy_cls in strategies:
                jobs.append(
                    {
                        "file_path": str(data_file),
                        "strategy_name": strategy_name.split(".")[-1],
                        "strategy_cls": strategy_cls,
                        "params": params or {},
                    }
                )

        if parallel:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = [executor.submit(self._run_single_job, job) for job in jobs]
                return [future.result() for future in as_completed(futures)]

        return [self._run_single_job(job) for job in jobs]

    def save_manifest(self, results: Sequence[Dict[str, Any]], manifest_path: Optional[Path] = None) -> Path:
        manifest_path = Path(manifest_path or self.results_dir / "batch_manifest.json")
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(list(results), indent=2), encoding="utf-8")
        return manifest_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Recursive, parallel batch backtest runner")
    parser.add_argument("--data-dir", type=Path, default=None, help="Path to input CSV data directory")
    parser.add_argument("--strategies-dir", type=Path, default=None, help="Path to strategies directory")
    parser.add_argument("--results-dir", type=Path, default=None, help="Path to save results")
    parser.add_argument("--max-workers", type=int, default=4, help="Maximum worker threads")
    parser.add_argument("--max-strategies", type=int, default=None, help="Maximum strategies to run")
    parser.add_argument("--data-pattern", default="*.csv", help="Glob pattern for data files")
    parser.add_argument("--no-parallel", action="store_true", help="Run jobs sequentially")
    parser.add_argument("--recursive", action="store_true", default=True, help="Enable recursive discovery for data files")
    parser.add_argument("--no-recursive", action="store_false", dest="recursive", help="Disable recursive discovery for data files")
    parser.add_argument("--manifest", default=None, help="Path to save the batch manifest JSON")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runner = BatchBacktestRunner(
        data_dir=args.data_dir,
        strategies_dir=args.strategies_dir,
        results_dir=args.results_dir,
        max_workers=args.max_workers,
        recursive=args.recursive,
    )
    results = runner.run(
        max_strategies=args.max_strategies,
        data_pattern=args.data_pattern,
        parallel=not args.no_parallel,
    )
    if args.manifest:
        runner.save_manifest(results, Path(args.manifest))
    print(f"Completed {len(results)} jobs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
