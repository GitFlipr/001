from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def get_default_data_dir() -> Path:
    return PROJECT_ROOT / "data" / "Hyperliquid"


def get_default_strategies_dir() -> Path:
    return PROJECT_ROOT / "strategies"


def get_default_results_dir() -> Path:
    return Path(r"D:\Results")


def ensure_directories() -> None:
    for path in [get_default_data_dir(), get_default_strategies_dir(), get_default_results_dir()]:
        path.mkdir(parents=True, exist_ok=True)
