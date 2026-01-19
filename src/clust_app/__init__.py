"""Interactive CDE clustering analysis dashboard.

This package provides a Dash-based interactive visualization tool for
clustering analysis of Common Data Element (CDE) embeddings.

Main entry point:
    clust-app (console command)

Programmatic usage:
    from clust_app.app import InteractiveClusteringAnalyzer, main

    analyzer = InteractiveClusteringAnalyzer()
    # ... configure and run
"""

__version__ = "0.1.0"

from clust_app.app import InteractiveClusteringAnalyzer, main

__all__ = [
    "__version__",
    "InteractiveClusteringAnalyzer",
    "main",
]
