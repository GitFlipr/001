from __future__ import annotations

import shutil
from pathlib import Path
import re

ROOT = Path(r"c:\Users\andre\Desktop\Mastercode")
BACKUP_DIR = ROOT / "Strategies" / "Backup"
DEST_ROOT = ROOT / "Backtesting" / "NewBacktesting" / "strategies"

CATEGORY_MAP = [
    (re.compile(r"trend|ema|macd|adx|sma|ma_|slow|triple|carry|venge|adaptive|execution|kalman|parabolic|golden|death|stacked|dual"), "trend_following"),
    (re.compile(r"breakout|boll|band|keltner|donchian|resistance|pivot|range|channel|harami|engulfing|hammer|inside|morning|piercing|darkcloud|shooting|tweezer|three_white|three_black|candle|doji|support|break"), "breakout"),
    (re.compile(r"mean|rsi|reversion|revert|stochastic|oscillator|divergence|bounce|oversold|overbought"), "mean_reversion"),
    (re.compile(r"momentum|roc|impulse|explosion|rejection|cycle|rocket|parabolic|volume_price"), "momentum"),
    (re.compile(r"scalp|scalper|simple|grid|silver|bullet|fibonacci|fib|high_freq|hft|microstructure|quiet|residual|range_liquidity|spread|pl_dot|vwap|vol_spike|volatility_breakout|vol_regime|vol_spike|gann|liquidity"), "scalping"),
    (re.compile(r"season|calendar|month|date"), "seasonality"),
    (re.compile(r"volume|vwap|flow|volume_price|volume_spread"), "volume"),
    (re.compile(r"volatility|vol|risk|regime|high_vol|low_vol|neutral|statistical|arbitrage"), "volatility_risk"),
]

SKIP_NAMES = {
    "backtest_utils.py",
    "77_backtest.py",
    "15m_backtesting.py",
    "compound_growth.py",
    "ENHANCED_SCALPING_README.md",
}


def fallback_category(name: str) -> str:
    lower = name.lower()
    for pattern, category in CATEGORY_MAP:
        if pattern.search(lower):
            return category
    return "misc"


def copy_strategy_files() -> list[Path]:
    created: list[Path] = []
    if not BACKUP_DIR.exists():
        raise FileNotFoundError(f"Backup directory not found: {BACKUP_DIR}")

    for source_file in sorted(BACKUP_DIR.glob("*.py")):
        if source_file.name in SKIP_NAMES:
            continue
        if source_file.name.startswith("__"):
            continue

        category = fallback_category(source_file.name)
        target_dir = DEST_ROOT / category
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file = target_dir / source_file.name
        shutil.copy2(source_file, target_file)
        created.append(target_file)

    for category_dir in sorted((DEST_ROOT).iterdir()):
        if not category_dir.is_dir():
            continue
        py_files = [p.name for p in category_dir.glob("*.py") if p.name != "__init__.py"]
        init_path = category_dir / "__init__.py"
        if not init_path.exists():
            init_path.write_text('"""Auto-migrated strategies from the legacy backup folder."""\n\n', encoding="utf-8")
        init_lines = ["\n", '"""Auto-migrated strategies from the legacy backup folder."""\n']
        for py_file in py_files:
            module_name = py_file[:-3]
            init_lines.append(f"from .{module_name} import *\n")
        init_lines.append("\n__all__ = [name for name in globals() if not name.startswith('_')]\n")
        init_path.write_text("".join(init_lines), encoding="utf-8")

    return created


if __name__ == "__main__":
    created = copy_strategy_files()
    print(f"Copied {len(created)} strategy files into {DEST_ROOT}")
    for path in created[:20]:
        print(path.relative_to(ROOT))
