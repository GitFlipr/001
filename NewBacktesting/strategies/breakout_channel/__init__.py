
"""Auto-migrated strategies from the legacy backup folder."""
from importlib import import_module

_MODULES = [
    "new_breakout_channel_strategies",
]

for module_name in _MODULES:
    try:
        module = import_module(f".{module_name}", __name__)
    except Exception:
        continue
    globals().update({name: getattr(module, name) for name in dir(module) if not name.startswith("_")})

__all__ = sorted({name for name in globals() if not name.startswith("_") and name not in {"import_module", "module", "module_name", "_MODULES"}})
