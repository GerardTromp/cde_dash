"""HDBSCAN clustering method."""

from typing import Dict, Any, Tuple
import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import HDBSCAN  # type: ignore

from ..registry import MethodRegistry


@MethodRegistry.register_clustering
class HDBSCANMethod:
    """HDBSCAN (Hierarchical Density-Based Spatial Clustering)."""

    name = "HDBSCAN"
    method_id = "hdbscan"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default HDBSCAN parameters."""
        return {
            "min_cluster_size": 15,
            "min_samples": 5,
            "cluster_selection_method": "eom",
            "cluster_selection_epsilon": 0.0,
            "metric": "euclidean",
            "alpha": 1.0,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            # Tier 1 - Essential (always visible)
            "min_cluster_size": {
                "type": "int",
                "default": 15,
                "min": 2,
                "max": 100,
                "description": "Minimum cluster size (lower = more small clusters)",
                "tier": 1,
            },
            "min_samples": {
                "type": "int",
                "default": 5,
                "min": 1,
                "max": 50,
                "description": "Minimum samples in neighborhood for core points",
                "tier": 1,
            },
            # Tier 2 - Important (expandable)
            "cluster_selection_method": {
                "type": "select",
                "default": "eom",
                "options": ["eom", "leaf"],
                "description": "Selection method ('leaf' better for many small clusters)",
                "tier": 2,
                "highlight": True,
            },
            "cluster_selection_epsilon": {
                "type": "float",
                "default": 0.0,
                "min": 0.0,
                "max": 0.5,
                "step": 0.001,
                "description": "Distance threshold for cluster merging (lower = more clusters)",
                "tier": 2,
                "highlight": True,
            },
            # Tier 3 - Advanced (nested under Tier 2)
            "metric": {
                "type": "select",
                "default": "euclidean",
                "options": ["euclidean", "manhattan", "cosine"],
                "description": "Distance metric",
                "tier": 3,
            },
            "alpha": {
                "type": "float",
                "default": 1.0,
                "min": 0.1,
                "max": 2.0,
                "step": 0.1,
                "description": "Distance scaling parameter",
                "tier": 3,
            },
        }

    def fit_predict(
        self, embeddings: NDArray[np.float64], params: Dict[str, Any]
    ) -> Tuple[NDArray[np.int64], Any]:
        """Apply HDBSCAN clustering.

        Args:
            embeddings: 2D embeddings (n_samples, 2)
            params: HDBSCAN parameters

        Returns:
            Tuple of (cluster_labels, clusterer_object)
        """
        full_params = {**self.default_params(), **params}

        clusterer = HDBSCAN(
            min_cluster_size=full_params["min_cluster_size"],
            min_samples=full_params["min_samples"],
            cluster_selection_method=full_params["cluster_selection_method"],
            cluster_selection_epsilon=full_params["cluster_selection_epsilon"],
            metric=full_params["metric"],
            alpha=full_params["alpha"],
        )
        labels = clusterer.fit_predict(embeddings)
        return labels, clusterer
