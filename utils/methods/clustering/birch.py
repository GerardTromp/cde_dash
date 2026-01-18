"""BIRCH clustering method."""

from typing import Dict, Any, Tuple
import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import Birch  # type: ignore

from ..registry import MethodRegistry


@MethodRegistry.register_clustering
class BIRCHMethod:
    """BIRCH (Balanced Iterative Reducing and Clustering using Hierarchies).

    BIRCH is designed for large datasets and is memory-efficient.
    Very fast on ~30k points. Good for many small clusters when using
    low threshold values.
    """

    name = "BIRCH"
    method_id = "birch"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default BIRCH parameters."""
        return {
            "threshold": 0.3,
            "n_clusters": 50,
            "branching_factor": 50,
            "compute_labels": True,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation.

        Based on wireframe guidance for ~30k points with many small clusters:
        - threshold controls CF-tree granularity (lower = more subclusters)
        - n_clusters for final agglomeration (set high or None for many clusters)
        - branching_factor affects tree structure and memory
        """
        return {
            # Tier 1 - Essential (always visible)
            "threshold": {
                "type": "float",
                "default": 0.3,
                "min": 0.01,
                "max": 2.0,
                "step": 0.05,
                "description": "CF-tree threshold (lower = more small clusters, try 0.1-0.3)",
                "tier": 1,
                "highlight": True,
            },
            "n_clusters": {
                "type": "int",
                "default": 50,
                "min": 2,
                "max": 500,
                "description": "Number of final clusters (set high for many small clusters)",
                "tier": 1,
                "highlight": True,
            },
            # Tier 2 - Important (expandable)
            "branching_factor": {
                "type": "int",
                "default": 50,
                "min": 10,
                "max": 200,
                "description": "Max children per node (lower values for many small clusters)",
                "tier": 2,
            },
            # Tier 3 - Advanced (nested under Tier 2)
            "compute_labels": {
                "type": "bool",
                "default": True,
                "description": "Compute cluster labels at the end",
                "tier": 3,
            },
        }

    def fit_predict(
        self, embeddings: NDArray[np.float64], params: Dict[str, Any]
    ) -> Tuple[NDArray[np.int64], Any]:
        """Apply BIRCH clustering.

        Args:
            embeddings: 2D embeddings (n_samples, 2)
            params: BIRCH parameters

        Returns:
            Tuple of (cluster_labels, clusterer_object)
        """
        full_params = {**self.default_params(), **params}

        # Handle n_clusters - can be None to let subclusters be final clusters
        n_clusters = full_params["n_clusters"]
        if n_clusters is not None and n_clusters <= 0:
            n_clusters = None

        clusterer = Birch(
            threshold=full_params["threshold"],
            n_clusters=n_clusters,
            branching_factor=full_params["branching_factor"],
            compute_labels=full_params["compute_labels"],
        )
        labels = clusterer.fit_predict(embeddings)
        return labels, clusterer
