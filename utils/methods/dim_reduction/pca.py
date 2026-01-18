"""PCA dimension reduction method."""

from typing import Dict, Any
import numpy as np
from numpy.typing import NDArray
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from ..registry import MethodRegistry


@MethodRegistry.register_dim_reduction
class PCAMethod:
    """PCA (Principal Component Analysis) dimension reduction."""

    name = "PCA"
    method_id = "pca"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default PCA parameters."""
        return {
            "n_components": 2,
            "whiten": False,
            "svd_solver": "auto",
            "random_state": 42,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            "whiten": {
                "type": "bool",
                "default": False,
                "description": "Normalize components to unit variance",
            },
            "svd_solver": {
                "type": "select",
                "default": "auto",
                "options": ["auto", "full", "arpack", "randomized"],
                "description": "SVD solver algorithm",
            },
        }

    def fit_transform(
        self, embeddings: NDArray[np.float64], params: Dict[str, Any]
    ) -> NDArray[np.float64]:
        """Apply PCA dimension reduction.

        Args:
            embeddings: High-dimensional embeddings (n_samples, n_features)
            params: PCA parameters

        Returns:
            2D embeddings (n_samples, 2)
        """
        full_params = {**self.default_params(), **params}

        # Standardize embeddings
        scaler = StandardScaler()
        scaled = scaler.fit_transform(embeddings)

        # Apply PCA
        pca = PCA(
            n_components=full_params["n_components"],
            whiten=full_params["whiten"],
            svd_solver=full_params["svd_solver"],
            random_state=full_params["random_state"],
        )
        return pca.fit_transform(scaled)
