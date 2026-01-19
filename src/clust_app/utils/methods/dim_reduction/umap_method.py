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
            "spread": 1.0,
            "n_epochs": 200,
            "negative_sample_rate": 5,
            "n_components": 2,
            "random_state": 42,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            # Tier 1 - Essential (always visible)
            "n_neighbors": {
                "type": "int",
                "default": 15,
                "min": 2,
                "max": 200,
                "description": "Number of neighbors for local structure",
                "tier": 1,
            },
            "min_dist": {
                "type": "float",
                "default": 0.1,
                "min": 0.0,
                "max": 1.0,
                "step": 0.05,
                "description": "Minimum distance between points in embedding",
                "tier": 1,
            },
            # Tier 2 - Important (expandable)
            "n_components": {
                "type": "int",
                "default": 2,
                "min": 2,
                "max": 10,
                "description": "Number of dimensions in output embedding",
                "tier": 2,
            },
            "metric": {
                "type": "select",
                "default": "cosine",
                "options": ["cosine", "euclidean", "manhattan", "correlation"],
                "description": "Distance metric",
                "tier": 2,
            },
            "spread": {
                "type": "float",
                "default": 1.0,
                "min": 0.1,
                "max": 5.0,
                "step": 0.1,
                "description": "Scale of embedded points spread",
                "tier": 2,
            },
            # Tier 3 - Advanced (nested under Tier 2)
            "n_epochs": {
                "type": "int",
                "default": 200,
                "min": 50,
                "max": 1000,
                "step": 50,
                "description": "Number of training epochs",
                "tier": 3,
            },
            "negative_sample_rate": {
                "type": "int",
                "default": 5,
                "min": 1,
                "max": 20,
                "description": "Negative samples per positive sample",
                "tier": 3,
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
            spread=full_params["spread"],
            n_epochs=full_params["n_epochs"],
            negative_sample_rate=full_params["negative_sample_rate"],
            n_components=full_params["n_components"],
            random_state=full_params["random_state"],
        )
        return reducer.fit_transform(scaled)
