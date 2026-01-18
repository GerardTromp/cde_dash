"""Protocol definitions for dimension reduction and clustering methods."""

from typing import Protocol, Dict, Any, Tuple, runtime_checkable
import numpy as np
from numpy.typing import NDArray


@runtime_checkable
class DimReductionMethod(Protocol):
    """Protocol for dimension reduction methods."""

    name: str  # Display name (e.g., "UMAP")
    method_id: str  # Registry key (e.g., "umap")

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default parameters for this method."""
        ...

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation.

        Each parameter entry should have:
        - type: "int", "float", "bool", or "select"
        - default: default value
        - description: human-readable description
        - For numeric types: min, max, step (optional)
        - For select type: options (list of valid values)
        """
        ...

    def fit_transform(
        self, embeddings: NDArray[np.float64], params: Dict[str, Any]
    ) -> NDArray[np.float64]:
        """Apply dimension reduction to embeddings."""
        ...


@runtime_checkable
class ClusteringMethod(Protocol):
    """Protocol for clustering methods."""

    name: str  # Display name (e.g., "HDBSCAN")
    method_id: str  # Registry key (e.g., "hdbscan")

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default parameters for this method."""
        ...

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        ...

    def fit_predict(
        self, embeddings: NDArray[np.float64], params: Dict[str, Any]
    ) -> Tuple[NDArray[np.int64], Any]:
        """Apply clustering to embeddings.

        Returns:
            Tuple of (cluster_labels, clusterer_object)
        """
        ...
