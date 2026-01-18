"""UMAP dimension reduction method."""

from typing import Dict, Any
import numpy as np
from numpy.typing import NDArray
import umap  # type: ignore
from sklearn.preprocessing import StandardScaler

from ..registry import MethodRegistry


@MethodRegistry.register_dim_reduction
class UMAPMethod:
    """UMAP (Uniform Manifold Approximation and Projection) dimension reduction."""

    name = "UMAP"
    method_id = "umap"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default UMAP parameters."""
        return {
            "n_neighbors": 15,
            "min_dist": 0.1,
            "metric": "cosine",
            "n_components": 2,
            "random_state": 42,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            "n_neighbors": {
                "type": "int",
                "default": 15,
                "min": 2,
                "max": 200,
                "description": "Number of neighbors for local structure",
            },
            "min_dist": {
                "type": "float",
                "default": 0.1,
                "min": 0.0,
                "max": 1.0,
                "step": 0.05,
                "description": "Minimum distance between points in embedding",
            },
            "metric": {
                "type": "select",
                "default": "cosine",
                "options": ["cosine", "euclidean", "manhattan", "correlation"],
                "description": "Distance metric",
            },
        }

    def fit_transform(
        self, embeddings: NDArray[np.float64], params: Dict[str, Any]
    ) -> NDArray[np.float64]:
        """Apply UMAP dimension reduction.

        Args:
            embeddings: High-dimensional embeddings (n_samples, n_features)
            params: UMAP parameters

        Returns:
            2D embeddings (n_samples, 2)
        """
        full_params = {**self.default_params(), **params}

        # Adjust n_neighbors to not exceed data size
        max_neighbors = max(2, len(embeddings) // 3)
        full_params["n_neighbors"] = min(full_params["n_neighbors"], max_neighbors)

        # Standardize embeddings
        scaler = StandardScaler()
        scaled = scaler.fit_transform(embeddings)

        # Apply UMAP
        reducer = umap.UMAP(
            n_neighbors=full_params["n_neighbors"],
            min_dist=full_params["min_dist"],
            metric=full_params["metric"],
            n_components=full_params["n_components"],
            random_state=full_params["random_state"],
        )
        return reducer.fit_transform(scaled)
