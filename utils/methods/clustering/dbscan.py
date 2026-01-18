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
            "algorithm": "auto",
            "leaf_size": 30,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            # Tier 1 - Essential (always visible)
            "eps": {
                "type": "float",
                "default": 0.5,
                "min": 0.01,
                "max": 10.0,
                "step": 0.1,
                "description": "Maximum distance between samples in neighborhood",
                "tier": 1,
            },
            "min_samples": {
                "type": "int",
                "default": 5,
                "min": 1,
                "max": 50,
                "description": "Minimum samples for core points (lower = more small clusters)",
                "tier": 1,
            },
            # Tier 2 - Important (expandable)
            "metric": {
                "type": "select",
                "default": "euclidean",
                "options": ["euclidean", "manhattan", "cosine"],
                "description": "Distance metric",
                "tier": 2,
            },
            "algorithm": {
                "type": "select",
                "default": "auto",
                "options": ["auto", "ball_tree", "kd_tree", "brute"],
                "description": "Algorithm for nearest neighbors (ball_tree/kd_tree faster)",
                "tier": 2,
            },
            # Tier 3 - Advanced (nested under Tier 2)
            "leaf_size": {
                "type": "int",
                "default": 30,
                "min": 10,
                "max": 100,
                "description": "Leaf size for ball_tree/kd_tree",
                "tier": 3,
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
            algorithm=full_params["algorithm"],
            leaf_size=full_params["leaf_size"],
        )
        labels = clusterer.fit_predict(embeddings)
        return labels, clusterer
