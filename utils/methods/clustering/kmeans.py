"""K-Means clustering method."""

from typing import Dict, Any, Tuple
import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import KMeans

from ..registry import MethodRegistry


@MethodRegistry.register_clustering
class KMeansMethod:
    """K-Means clustering algorithm."""

    name = "K-Means"
    method_id = "kmeans"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default K-Means parameters."""
        return {
            "n_clusters": 8,
            "init": "k-means++",
            "n_init": 10,
            "max_iter": 300,
            "random_state": 42,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            "n_clusters": {
                "type": "int",
                "default": 8,
                "min": 2,
                "max": 50,
                "description": "Number of clusters to form",
            },
            "init": {
                "type": "select",
                "default": "k-means++",
                "options": ["k-means++", "random"],
                "description": "Initialization method for centroids",
            },
            "n_init": {
                "type": "int",
                "default": 10,
                "min": 1,
                "max": 50,
                "description": "Number of initializations to run",
            },
            "max_iter": {
                "type": "int",
                "default": 300,
                "min": 100,
                "max": 1000,
                "step": 100,
                "description": "Maximum iterations per initialization",
            },
        }

    def fit_predict(
        self, embeddings: NDArray[np.float64], params: Dict[str, Any]
    ) -> Tuple[NDArray[np.int64], Any]:
        """Apply K-Means clustering.

        Args:
            embeddings: 2D embeddings (n_samples, 2)
            params: K-Means parameters

        Returns:
            Tuple of (cluster_labels, clusterer_object)
        """
        full_params = {**self.default_params(), **params}

        # Ensure n_clusters doesn't exceed number of samples
        n_clusters = min(full_params["n_clusters"], len(embeddings))

        clusterer = KMeans(
            n_clusters=n_clusters,
            init=full_params["init"],
            n_init=full_params["n_init"],
            max_iter=full_params["max_iter"],
            random_state=full_params["random_state"],
        )
        labels = clusterer.fit_predict(embeddings)
        return labels, clusterer
