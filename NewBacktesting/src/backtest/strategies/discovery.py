"""
Strategy discovery and triage system.

Discovery priority
------------------
1. Explicit package list supplied by caller  → _load_from_packages
2. Auto sub-package scan (default)           → _discover_from_subpackages
   Each subfolder that has an __init__.py is imported as a package.
   Any name listed in __all__ that is a non-abstract Strategy subclass
   is collected.  This avoids importing the ~390 legacy files that still
   inherit from the third-party `backtesting` library instead of
   backtest.strategies.base.Strategy.
3. Fallback: brute-force file scan           → _discover_from_directory
   Only used if sub-package scan finds nothing (e.g. no __init__.py files).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Type
from pathlib import Path
import importlib
import inspect
import json
import sys

from .base import Strategy
from backtest.config import get_default_strategies_dir


class StrategyDiscovery:
    """Strategy discovery and loading."""

    def __init__(
        self,
        discovery_root: Optional[Path] = None,
        triage_manifest_path: Optional[Path] = None,
        skip_statuses: Optional[List[str]] = None,
    ) -> None:
        self.discovery_root = Path(discovery_root or get_default_strategies_dir())
        self.triage_manifest_path = triage_manifest_path
        self.skip_statuses = skip_statuses or ["retire", "quarantine"]
        self._skip_modules: Optional[set] = None

    # ------------------------------------------------------------------
    # Triage manifest helpers
    # ------------------------------------------------------------------

    def _load_triage_manifest(self) -> Dict[str, Any]:
        if not self.triage_manifest_path or not self.triage_manifest_path.is_file():
            return {}
        try:
            data = json.loads(self.triage_manifest_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _get_skip_modules(self) -> set:
        if self._skip_modules is not None:
            return self._skip_modules
        self._skip_modules = set()
        manifest = self._load_triage_manifest()
        for item in manifest.get("strategies", []):
            if not isinstance(item, dict):
                continue
            status = str(item.get("status", "")).strip().lower()
            module = str(item.get("module", "")).strip()
            if module and status in self.skip_statuses:
                self._skip_modules.add(module)
        return self._skip_modules

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def discover_strategies(
        self,
        strategy_packages: Optional[List[str]] = None,
        max_strategies: Optional[int] = None,
    ) -> List[Tuple[str, Type[Strategy]]]:
        """
        Return a list of (qualified_name, StrategyClass) tuples.

        Args:
            strategy_packages: Optional explicit list of importable package
                names (e.g. ``["strategies.trend_following"]``).  When given,
                only those packages are scanned.
            max_strategies: Cap on the number of strategies returned.
        """
        # Priority 1 — explicit package list
        if strategy_packages:
            return self._load_from_packages(strategy_packages, max_strategies)

        # Priority 2 — auto sub-package scan (fast, accurate)
        # Always run even if top-level package already returned some classes,
        # because subpackages may export additional non-duplicate strategies.
        found = self._discover_from_subpackages(max_strategies)
        return found

    # ------------------------------------------------------------------
    # Method 1: explicit package list
    # ------------------------------------------------------------------

    def _load_from_packages(
        self,
        packages: List[str],
        max_strategies: Optional[int] = None,
    ) -> List[Tuple[str, Type[Strategy]]]:
        discovered: List[Tuple[str, Type[Strategy]]] = []
        seen: set = set()
        skip_modules = self._get_skip_modules()

        for pkg in packages:
            if pkg in skip_modules:
                continue
            try:
                mod = importlib.import_module(pkg)
            except Exception as exc:
                print(f"[Discovery] Could not import package {pkg!r}: {exc}")
                continue

            for name in list(getattr(mod, "__all__", [])):
                export_name = f"{pkg}.{name}"
                if export_name in seen or export_name in skip_modules:
                    continue
                cls = getattr(mod, name, None)
                if not self._is_valid_strategy(cls):
                    continue
                seen.add(export_name)
                discovered.append((export_name, cls))
                if max_strategies and len(discovered) >= max_strategies:
                    return discovered

        return discovered

    # ------------------------------------------------------------------
    # Method 2: auto sub-package scan  ← PRIMARY PATH
    # ------------------------------------------------------------------

    def _discover_from_subpackages(
        self,
        max_strategies: Optional[int] = None,
    ) -> List[Tuple[str, Type[Strategy]]]:
        """
        Import every direct subfolder of discovery_root that contains an
        __init__.py, then collect Strategy subclasses from its __all__.
        """
        if not self.discovery_root.is_dir():
            return []

        # Ensure the *parent* of discovery_root is on sys.path so that
        # "strategies" is importable as a top-level package.
        root_parent = str(self.discovery_root.parent.resolve())
        if root_parent not in sys.path:
            sys.path.insert(0, root_parent)

        # Bust any stale negative cache entries (e.g. if strategies was
        # partially imported before the correct path was on sys.path).
        pkg_base = self.discovery_root.name   # e.g. "strategies"
        for key in list(sys.modules.keys()):
            if key == pkg_base or key.startswith(pkg_base + "."):
                del sys.modules[key]

        skip_dirs = {"storage", "winners", "__pycache__"}
        skip_modules = self._get_skip_modules()

        discovered: List[Tuple[str, Type[Strategy]]] = []
        seen: set = set()

        # Also try the top-level strategies/__init__.py itself
        subpackages: List[str] = [pkg_base]

        # Collect all sub-packages (one level deep is enough — each
        # subfolder's __init__.py re-exports everything it needs)
        for child in sorted(self.discovery_root.iterdir()):
            if not child.is_dir():
                continue
            if child.name in skip_dirs or child.name.startswith("."):
                continue
            if not (child / "__init__.py").exists():
                continue
            subpackages.append(f"{pkg_base}.{child.name}")

        for pkg_name in subpackages:
            if pkg_name in skip_modules:
                continue
            try:
                mod = importlib.import_module(pkg_name)
            except Exception as exc:
                print(f"[Discovery] Skipping {pkg_name!r}: {exc}")
                continue

            exported_names = list(getattr(mod, "__all__", []))
            if not exported_names:
                # No __all__ — scan module namespace directly
                exported_names = [n for n in dir(mod) if not n.startswith("_")]

            for name in exported_names:
                cls = getattr(mod, name, None)
                if not self._is_valid_strategy(cls):
                    continue
                # Use the canonical class module so duplicates across
                # packages are deduplicated by class identity
                canon = f"{cls.__module__}.{cls.__qualname__}"
                if canon in seen:
                    continue
                seen.add(canon)
                label = f"{pkg_name}.{name}"
                discovered.append((label, cls))
                if max_strategies and len(discovered) >= max_strategies:
                    return discovered

        return discovered

    # ------------------------------------------------------------------
    # Method 3: brute-force file scan (fallback)
    # ------------------------------------------------------------------

    def _discover_from_directory(
        self,
        max_strategies: Optional[int] = None,
    ) -> List[Tuple[str, Type[Strategy]]]:
        """
        Walk every .py file under discovery_root and import it, looking for
        Strategy subclasses.  Slow and noisy but catches anything not wired
        into an __init__.py.
        """
        discovered: List[Tuple[str, Type[Strategy]]] = []
        seen: set = set()
        skip_modules = self._get_skip_modules()
        skip_top_dirs = {"storage", "winners"}
        duplicate_suffixes = ("_dup1", "_dup2", "_dup3", "_dup4", "_dup5")

        if not self.discovery_root.is_dir():
            return discovered

        root_parent = str(self.discovery_root.parent)
        if root_parent not in sys.path:
            sys.path.insert(0, root_parent)

        module_base = self.discovery_root.name

        for py_path in sorted(self.discovery_root.rglob("*.py")):
            if not py_path.is_file() or py_path.name == "__init__.py":
                continue
            try:
                rel = py_path.relative_to(self.discovery_root)
            except ValueError:
                continue
            if any(part in skip_top_dirs for part in rel.parts):
                continue
            if any(py_path.stem.lower().endswith(s) for s in duplicate_suffixes):
                continue

            mod_name = module_base + "." + ".".join(rel.with_suffix("").parts)
            if mod_name in skip_modules:
                continue

            try:
                mod = importlib.import_module(mod_name)
            except Exception:
                continue

            for attr_name, attr in vars(mod).items():
                if not self._is_valid_strategy(attr):
                    continue
                canon = f"{attr.__module__}.{attr.__qualname__}"
                if canon in seen:
                    continue
                seen.add(canon)
                discovered.append((f"{mod_name}.{attr_name}", attr))
                if max_strategies and len(discovered) >= max_strategies:
                    return discovered

        return discovered

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    @staticmethod
    def _is_valid_strategy(cls: Any) -> bool:
        """Return True if cls is a concrete, non-abstract Strategy subclass."""
        if cls is None or cls is Strategy:
            return False
        if not isinstance(cls, type):
            return False
        try:
            if not issubclass(cls, Strategy):
                return False
        except TypeError:
            return False
        if inspect.isabstract(cls):
            return False
        return True
