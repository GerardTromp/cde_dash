"""Spectral clustering method."""

from typing import Dict, Any, Tuple
import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import SpectralClustering

from ..registry import MethodRegistry


@MethodRegistry.register_clustering
class SpectralMethod:
    """Spectral clustering using graph Laplacian eigenvectors."""

    name = "Spectral"
    method_id = "spectral"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default Spectral clustering parameters."""
        return {
            "n_clusters": 8,
            "affinity": "nearest_neighbors",
            "n_neighbors": 10,
            "assign_labels": "kmeans",
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
            "affinity": {
                "type": "select",
                "default": "nearest_neighbors",
                "options": ["nearest_neighbors", "rbf"],
                "description": "Affinity matrix construction method",
            },
            "n_neighbors": {
                "type": "int",
                "default": 10,
                "min": 2,
                "max": 50,
                "description": "Number of neighbors (for nearest_neighbors affinity)",
            },
            "assign_labels": {
                "type": "select",
                "default": "kmeans",
                "options": ["kmeans", "discretize", "cluster_qr"],
                "description": "Label assignment strategy",
            },
        }

    def fit_predict(
        self, embeddings: NDArray[np.float64], params: Dict[str, Any]
    ) -> Tuple[NDArray[np.int64], Any]:
        """Apply Spectral clustering.

        Args:
            embeddings: 2D embeddings (n_samples, 2)
            params: Spectral clustering parameters

        Returns:
            Tuple of (cluster_labels, clusterer_object)
        """
        full_params = {**self.default_params(), **params}

        # Ensure n_clusters and n_neighbors don't exceed number of samples
        n_samples = len(embeddings)
        n_clusters = min(full_params["n_clusters"], n_samples)
        n_neighbors = min(full_params["n_neighbors"], n_samples - 1)

        clusterer = SpectralClustering(
            n_clusters=n_clusters,
            affinity=full_params["affinity"],
            n_neighbors=n_neighbors,
            assign_labels=full_params["assign_labels"],
            random_state=full_params["random_state"],
        )
        labels = clusterer.fit_predict(embeddings)
        return labels, clusterer
