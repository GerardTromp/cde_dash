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
            "metric": "euclidean",
            "cluster_selection_method": "eom",
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            "min_cluster_size": {
                "type": "int",
                "default": 15,
                "min": 2,
                "max": 100,
                "description": "Minimum cluster size",
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
            "cluster_selection_method": {
                "type": "select",
                "default": "eom",
                "options": ["eom", "leaf"],
                "description": "Cluster selection method (eom=Excess of Mass)",
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
            metric=full_params["metric"],
            cluster_selection_method=full_params["cluster_selection_method"],
        )
        labels = clusterer.fit_predict(embeddings)
        return labels, clusterer
