"""DBSCAN clustering method."""

from typing import Dict, Any, Tuple
import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import DBSCAN

from ..registry import MethodRegistry


@MethodRegistry.register_clustering
class DBSCANMethod:
    """DBSCAN (Density-Based Spatial Clustering of Applications with Noise)."""

    name = "DBSCAN"
    method_id = "dbscan"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default DBSCAN parameters."""
        return {
            "eps": 0.5,
            "min_samples": 5,
            "metric": "euclidean",
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            "eps": {
                "type": "float",
                "default": 0.5,
                "min": 0.01,
                "max": 10.0,
                "step": 0.1,
                "description": "Maximum distance between samples in neighborhood",
            },
            "min_samples": {
                "type": "int",
                "default": 5,
                "min": 1,
                "max": 50,
                "description": "Minimum samples in neighborhood for core points",
            },
            "metric": {
                "type": "select",
                "default": "euclidean",
                "options": ["euclidean", "manhattan", "cosine"],
                "description": "Distance metric",
            },
        }

    def fit_predict(
        self, embeddings: NDArray[np.float64], params: Dict[str, Any]
    ) -> Tuple[NDArray[np.int64], Any]:
        """Apply DBSCAN clustering.

        Args:
            embeddings: 2D embeddings (n_samples, 2)
            params: DBSCAN parameters

        Returns:
            Tuple of (cluster_labels, clusterer_object)
        """
        full_params = {**self.default_params(), **params}

        clusterer = DBSCAN(
            eps=full_params["eps"],
            min_samples=full_params["min_samples"],
            metric=full_params["metric"],
        )
        labels = clusterer.fit_predict(embeddings)
        return labels, clusterer
