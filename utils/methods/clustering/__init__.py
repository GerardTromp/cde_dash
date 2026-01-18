"""Clustering methods.

All methods in this package are automatically registered with MethodRegistry.
"""

from .hdbscan import HDBSCANMethod
from .dbscan import DBSCANMethod
from .kmeans import KMeansMethod
from .spectral import SpectralMethod
from .optics import OPTICSMethod
from .birch import BIRCHMethod

__all__ = [
    "HDBSCANMethod",
    "DBSCANMethod",
    "KMeansMethod",
    "SpectralMethod",
    "OPTICSMethod",
    "BIRCHMethod",
]
