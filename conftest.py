import sys, os, pathlib, warnings

ROOT = pathlib.Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))  # ensure top-level packages are importable

# Also make sure deep_research/komkom_scraper is on the path so that
#   `import komkom_scraper.spiders...` works even if the stub namespace
#   package fails to extend its path.
DEEP_DIR = ROOT / "deep_research" / "komkom_scraper"
if DEEP_DIR.exists() and str(DEEP_DIR) not in sys.path:
    sys.path.insert(0, str(DEEP_DIR))

warnings.filterwarnings("ignore", category=DeprecationWarning)

# --- Ensure scrapy sub-modules are available as attributes -----------------
import importlib
try:
    import scrapy  # noqa: WPS433 (external import inside try is fine here)
    for _sub in ("crawler", "settings"):
        if not hasattr(scrapy, _sub):
            setattr(scrapy, _sub, importlib.import_module(f"scrapy.{_sub}"))
except ModuleNotFoundError:
    # Scrapy is an optional dev dependency; the tests that rely on it will
    # be skipped automatically if it’s not installed.  We don’t enforce it.
    pass