# Root-level komkom_scraper package: forwards to deep_research/komkom_scraper/komkom_scraper
import os
import sys
import pkgutil

__path__ = pkgutil.extend_path(__path__, __name__)

# Search for the real komkom_scraper code up to two levels above this file
_root = os.path.dirname(os.path.abspath(__file__))

for up in range(3):
    base = os.path.abspath(os.path.join(_root, *(['..'] * up)))
    deep_path = os.path.join(base, "deep_research", "komkom_scraper", "komkom_scraper")
    if os.path.isdir(deep_path):
        if deep_path not in __path__:
            __path__.append(deep_path)
        parent = os.path.dirname(deep_path)
        if parent not in sys.path:
            sys.path.insert(0, parent)
        break