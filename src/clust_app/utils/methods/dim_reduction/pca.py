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
            "tol": 0.0,
            "iterated_power": 2,
            "random_state": 42,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            # Tier 2 - Important (PCA has fewer essential params)
            "n_components": {
                "type": "int",
                "default": 2,
                "min": 2,
                "max": 50,
                "description": "Number of principal components to keep",
                "tier": 2,
            },
            "whiten": {
                "type": "bool",
                "default": False,
                "description": "Normalize components to unit variance (useful before clustering)",
                "tier": 2,
            },
            "svd_solver": {
                "type": "select",
                "default": "auto",
                "options": ["auto", "full", "arpack", "randomized"],
                "description": "SVD solver ('randomized' faster for large data)",
                "tier": 2,
            },
            # Tier 3 - Advanced
            "tol": {
                "type": "float",
                "default": 0.0,
                "min": 0.0,
                "max": 1.0,
                "step": 0.001,
                "description": "Tolerance for singular values (arpack solver only)",
                "tier": 3,
            },
            "iterated_power": {
                "type": "int",
                "default": 2,
                "min": 0,
                "max": 10,
                "description": "Number of iterations for randomized solver",
                "tier": 3,
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
            tol=full_params["tol"],
            iterated_power=full_params["iterated_power"],
            random_state=full_params["random_state"],
        )
        return pca.fit_transform(scaled)
