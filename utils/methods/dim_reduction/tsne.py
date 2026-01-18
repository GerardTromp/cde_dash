"""t-SNE dimension reduction method."""

from typing import Dict, Any
import numpy as np
from numpy.typing import NDArray
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

from ..registry import MethodRegistry


@MethodRegistry.register_dim_reduction
class TSNEMethod:
    """t-SNE (t-Distributed Stochastic Neighbor Embedding) dimension reduction."""

    name = "t-SNE"
    method_id = "tsne"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default t-SNE parameters."""
        return {
            "perplexity": 30,
            "metric": "cosine",
            "method": "exact",
            "n_components": 2,
            "random_state": 42,
            "max_iter": 1000,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            "perplexity": {
                "type": "int",
                "default": 30,
                "min": 5,
                "max": 100,
                "description": "Perplexity (effective number of neighbors)",
            },
            "metric": {
                "type": "select",
                "default": "cosine",
                "options": ["cosine", "euclidean"],
                "description": "Distance metric",
            },
            "method": {
                "type": "select",
                "default": "exact",
                "options": ["exact", "barnes_hut"],
                "description": "Computation method (barnes_hut faster for large data)",
            },
            "max_iter": {
                "type": "int",
                "default": 1000,
                "min": 250,
                "max": 5000,
                "step": 250,
                "description": "Maximum iterations for optimization",
            },
        }

    def fit_transform(
        self, embeddings: NDArray[np.float64], params: Dict[str, Any]
    ) -> NDArray[np.float64]:
        """Apply t-SNE dimension reduction.

        Args:
            embeddings: High-dimensional embeddings (n_samples, n_features)
            params: t-SNE parameters

        Returns:
            2D embeddings (n_samples, 2)
        """
        full_params = {**self.default_params(), **params}

        # Adjust perplexity to not exceed data size
        max_perplexity = max(5, len(embeddings) // 4)
        full_params["perplexity"] = min(full_params["perplexity"], max_perplexity)

        # Standardize embeddings
        scaler = StandardScaler()
        scaled = scaler.fit_transform(embeddings)

        # Apply t-SNE
        tsne = TSNE(
            n_components=full_params["n_components"],
            perplexity=full_params["perplexity"],
            metric=full_params["metric"],
            method=full_params["method"],
            max_iter=full_params["max_iter"],
            random_state=full_params["random_state"],
        )
        return tsne.fit_transform(scaled)
