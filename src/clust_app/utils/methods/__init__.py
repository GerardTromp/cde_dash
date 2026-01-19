"""Method registry and modular analysis methods.

This package provides a registry-based architecture for dimension reduction
and clustering methods. Methods are automatically registered when imported.

Usage:
    from clust_app.utils.methods import MethodRegistry

    # List available methods
    dim_methods = MethodRegistry.list_dim_reduction()
    cluster_methods = MethodRegistry.list_clustering()

    # Get a method class
    umap_class = MethodRegistry.get_dim_reduction("umap")
    hdbscan_class = MethodRegistry.get_clustering("hdbscan")

    # Use a method
    reducer = umap_class()
    reduced = reducer.fit_transform(embeddings, params)
"""

from .registry import MethodRegistry
from .base import DimReductionMethod, ClusteringMethod

# Import subpackages to trigger method registration
from . import dim_reduction
from . import clustering

__all__ = [
    "MethodRegistry",
    "DimReductionMethod",
    "ClusteringMethod",
]
