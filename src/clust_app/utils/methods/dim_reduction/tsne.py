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
            "learning_rate": 200.0,
            "max_iter": 1000,
            "early_exaggeration": 12.0,
            "metric": "cosine",
            "method": "exact",
            "init": "pca",
            "n_components": 2,
            "random_state": 42,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            # Tier 1 - Essential (always visible)
            "perplexity": {
                "type": "int",
                "default": 30,
                "min": 5,
                "max": 100,
                "description": "Perplexity (effective number of neighbors)",
                "tier": 1,
            },
            # Tier 2 - Important (expandable)
            "n_components": {
                "type": "int",
                "default": 2,
                "min": 2,
                "max": 3,
                "description": "Number of dimensions in output embedding (2 or 3)",
                "tier": 2,
            },
            "learning_rate": {
                "type": "float",
                "default": 200.0,
                "min": 10.0,
                "max": 1000.0,
                "step": 10.0,
                "description": "Learning rate for optimization",
                "tier": 2,
            },
            "max_iter": {
                "type": "int",
                "default": 1000,
                "min": 250,
                "max": 5000,
                "step": 250,
                "description": "Maximum iterations for optimization",
                "tier": 2,
            },
            "early_exaggeration": {
                "type": "float",
                "default": 12.0,
                "min": 4.0,
                "max": 50.0,
                "step": 2.0,
                "description": "How tight clusters form early (higher = more separated)",
                "tier": 2,
            },
            # Tier 3 - Advanced (nested under Tier 2)
            "metric": {
                "type": "select",
                "default": "cosine",
                "options": ["cosine", "euclidean"],
                "description": "Distance metric",
                "tier": 3,
            },
            "method": {
                "type": "select",
                "default": "exact",
                "options": ["exact", "barnes_hut"],
                "description": "Computation method (barnes_hut faster for large data)",
                "tier": 3,
            },
            "init": {
                "type": "select",
                "default": "pca",
                "options": ["pca", "random"],
                "description": "Initialization method (pca is more stable)",
                "tier": 3,
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
            learning_rate=full_params["learning_rate"],
            max_iter=full_params["max_iter"],
            early_exaggeration=full_params["early_exaggeration"],
            metric=full_params["metric"],
            method=full_params["method"],
            init=full_params["init"],
            random_state=full_params["random_state"],
        )
        return tsne.fit_transform(scaled)
