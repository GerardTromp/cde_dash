"""Dimension reduction methods.

All methods in this package are automatically registered with MethodRegistry.
"""

from .umap_method import UMAPMethod
from .tsne import TSNEMethod
from .pca import PCAMethod

__all__ = ["UMAPMethod", "TSNEMethod", "PCAMethod"]
