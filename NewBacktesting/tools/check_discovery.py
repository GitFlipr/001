"""
Strategy & Data Discovery Diagnostic
=====================================
Run this from the project root to verify that batch runner will find
strategies and data files before kicking off a full run.

Usage (from Anaconda Prompt with backtesting env active):
    cd C:\\Users\\andre\\Desktop\\Mastercode\\Backtesting\\NewBacktesting
    python tools/check_discovery.py

Optional flags:
    --strategies-dir  PATH   override strategies directory
    --data-dir        PATH   override data directory
    --data-pattern    GLOB   default *.csv
    --verbose                print every discovered strategy name
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# ------------------------------------------------------------------ #
# Bootstrap sys.path so the script can be run from any working dir   #
# ------------------------------------------------------------------ #
_TOOLS_DIR   = Path(__file__).resolve().parent          # .../tools
_PROJECT_ROOT = _TOOLS_DIR.parent                        # .../NewBacktesting
_SRC_ROOT     = _PROJECT_ROOT / "src"

for _p in (_SRC_ROOT, _PROJECT_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from backtest.config import (
    get_default_data_dir,
    get_default_strategies_dir,
)
from backtest.strategies.discovery import StrategyDiscovery


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _bar(label: str, width: int = 60) -> str:
    return f"\n{'=' * width}\n  {label}\n{'=' * width}"


def check_strategies(strategies_dir: Path, verbose: bool) -> int:
    print(_bar("STRATEGY DISCOVERY"))
    print(f"  Root : {strategies_dir}")

    if not strategies_dir.exists():
        print(f"  [ERROR] Directory does not exist: {strategies_dir}")
        return 0

    # Count sub-packages (dirs with __init__.py)
    subpkgs = sorted(
        d.name for d in strategies_dir.iterdir()
        if d.is_dir() and (d / "__init__.py").exists() and not d.name.startswith("_")
    )
    print(f"  Sub-packages found : {len(subpkgs)}")
    for sp in subpkgs:
        print(f"    - {sp}")

    print()
    print("  Running StrategyDiscovery ...")
    t0 = time.perf_counter()
    discovery = StrategyDiscovery(discovery_root=strategies_dir)
    strategies = discovery.discover_strategies()
    elapsed = time.perf_counter() - t0

    print(f"  Strategies found   : {len(strategies)}  ({elapsed:.2f}s)")

    if not strategies:
        print()
        print("  [WARN] No strategies discovered.")
        print("         Possible causes:")
        print("           1. No __init__.py in strategy subfolders")
        print("           2. Classes don't inherit from backtest.strategies.base.Strategy")
        print("           3. sys.path doesn't include the project root")
        print(f"         sys.path[:4] = {sys.path[:4]}")
        return 0

    # Group by subfolder
    by_pkg: dict[str, list[str]] = {}
    for name, cls in strategies:
        pkg = name.split(".")[1] if "." in name else "root"
        by_pkg.setdefault(pkg, []).append(cls.__name__)

    print()
    for pkg, names in sorted(by_pkg.items()):
        print(f"  [{pkg}]  {len(names)} strategies")
        if verbose:
            for n in sorted(names):
                print(f"      {n}")

    if not verbose:
        print()
        print("  (use --verbose to list every strategy name)")

    return len(strategies)


def check_data(data_dir: Path, pattern: str) -> int:
    print(_bar("DATA DISCOVERY"))
    print(f"  Root    : {data_dir}")
    print(f"  Pattern : {pattern}")

    if not data_dir.exists():
        print(f"  [ERROR] Directory does not exist: {data_dir}")
        return 0

    files = sorted(data_dir.rglob(pattern))
    print(f"  Files found : {len(files)}")

    if not files:
        print("  [WARN] No data files found.")
        return 0

    # Group by immediate subdirectory
    by_subdir: dict[str, int] = {}
    for f in files:
        try:
            rel = f.relative_to(data_dir)
            subdir = rel.parts[0] if len(rel.parts) > 1 else "(root)"
        except ValueError:
            subdir = "(root)"
        by_subdir[subdir] = by_subdir.get(subdir, 0) + 1

    for subdir, count in sorted(by_subdir.items()):
        print(f"    {subdir:<30} {count:>5} files")

    return len(files)


def check_job_count(n_strategies: int, n_files: int) -> None:
    print(_bar("JOB ESTIMATE"))
    total = n_strategies * n_files
    print(f"  {n_strategies} strategies  x  {n_files} data files  =  {total:,} jobs")
    if total == 0:
        print("  [ERROR] No jobs will run — fix the issues above first.")
    elif total > 50_000:
        print(f"  [WARN] Large run — consider --max-strategies or a smaller data subset.")
    else:
        print("  Ready to run.")


# ------------------------------------------------------------------ #
# Main                                                                #
# ------------------------------------------------------------------ #

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Verify strategy and data discovery before a batch run."
    )
    parser.add_argument(
        "--strategies-dir", type=Path,
        default=get_default_strategies_dir(),
        help="Path to strategies folder (default: project strategies/)",
    )
    parser.add_argument(
        "--data-dir", type=Path,
        default=get_default_data_dir(),
        help="Path to data folder (default: data/Hyperliquid/)",
    )
    parser.add_argument(
        "--data-pattern", default="*.csv",
        help="Glob pattern for data files (default: *.csv)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print every discovered strategy name",
    )
    args = parser.parse_args()

    print("\nNewBacktesting — Discovery Check")
    print(f"Python  : {sys.version.split()[0]}")
    print(f"SRC     : {_SRC_ROOT}")
    print(f"PROJECT : {_PROJECT_ROOT}")

    n_strats = check_strategies(args.strategies_dir, args.verbose)
    n_files  = check_data(args.data_dir, args.data_pattern)
    check_job_count(n_strats, n_files)
    print()


if __name__ == "__main__":
    main()
