"""
pytest configuration — ensures src/ and the project root are on sys.path
so that `import backtest` and `import strategies` both work in tests.
"""
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent
_SRC_ROOT = _PROJECT_ROOT / "src"

for _p in (_SRC_ROOT, _PROJECT_ROOT):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
