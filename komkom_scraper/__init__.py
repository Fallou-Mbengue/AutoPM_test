# Namespace/forwarding package for komkom_scraper (root-level import support)
import os
import sys
import pkgutil

# Enable namespace package behavior
__path__ = pkgutil.extend_path(__path__, __name__)

# Compute the absolute path to the real komkom_scraper package
_repo_root = os.path.dirname(os.path.abspath(__file__))  # .../komkom_scraper/__init__.py
_deep_pkg = os.path.join(_repo_root, "deep_research", "komkom_scraper", "komkom_scraper")
# If run from repo root, _repo_root is correct. If run from deep_research/komkom_scraper, this is harmless.

# Try parent directories in case cwd is not repo root
for up in (0, 1, 2):
    try_path = os.path.abspath(os.path.join(_repo_root, *(['..'] * up), "deep_research", "komkom_scraper", "komkom_scraper"))
    if os.path.isdir(try_path):
        # Add to __path__ for package resolution
        if try_path not in __path__:
            __path__.append(try_path)
        # Add its parent to sys.path for module loading
        parent = os.path.dirname(try_path)
        if parent not in sys.path:
            sys.path.insert(0, parent)
        break