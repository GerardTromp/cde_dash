"""OPTICS clustering method."""

from typing import Dict, Any, Tuple
import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import OPTICS  # type: ignore

from ..registry import MethodRegistry


@MethodRegistry.register_clustering
class OPTICSMethod:
    """OPTICS (Ordering Points To Identify the Clustering Structure).

    OPTICS is excellent for varying density clusters. Good for datasets
    where clusters have different densities and sizes.
    """

    name = "OPTICS"
    method_id = "optics"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default OPTICS parameters."""
        return {
            "min_samples": 5,
            "xi": 0.05,
            "min_cluster_size": 10,
            "max_eps": float("inf"),
            "cluster_method": "xi",
            "metric": "euclidean",
            "p": 2,
            "algorithm": "auto",
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation.

        Based on wireframe guidance for ~30k points with many small clusters:
        - min_samples defines core points
        - xi controls cluster extraction steepness
        - min_cluster_size critical for many-small-clusters case
        """
        return {
            # Tier 1 - Essential (always visible)
            "min_samples": {
                "type": "int",
                "default": 5,
                "min": 2,
                "max": 50,
                "description": "Minimum samples in neighborhood for core points",
                "tier": 1,
            },
            "xi": {
                "type": "float",
                "default": 0.05,
                "min": 0.0,
                "max": 1.0,
                "step": 0.01,
                "description": "Cluster extraction steepness (lower = more clusters)",
                "tier": 1,
                "highlight": True,
            },
            "min_cluster_size": {
                "type": "int",
                "default": 10,
                "min": 2,
                "max": 100,
                "description": "Minimum cluster size (set low for many small clusters)",
                "tier": 1,
                "highlight": True,
            },
            # Tier 2 - Important (expandable)
            "max_eps": {
                "type": "float",
                "default": float("inf"),
                "min": 0.0,
                "max": 100.0,
                "step": 0.5,
                "description": "Maximum distance for neighbors (inf = no limit, lower = faster)",
                "tier": 2,
            },
            "cluster_method": {
                "type": "select",
                "default": "xi",
                "options": ["xi", "dbscan"],
                "description": "Cluster extraction method ('xi' often better for heterogeneous sizes)",
                "tier": 2,
                "highlight": True,
            },
            # Tier 3 - Advanced (nested under Tier 2)
            "metric": {
                "type": "select",
                "default": "euclidean",
                "options": ["euclidean", "manhattan", "cosine", "minkowski"],
                "description": "Distance metric",
                "tier": 3,
            },
            "p": {
                "type": "int",
                "default": 2,
                "min": 1,
                "max": 5,
                "description": "Minkowski metric p-parameter (1=manhattan, 2=euclidean)",
                "tier": 3,
            },
            "algorithm": {
                "type": "select",
                "default": "auto",
                "options": ["auto", "ball_tree", "kd_tree", "brute"],
                "description": "Nearest neighbors algorithm",
                "tier": 3,
            },
        }

    def fit_predict(
        self, embeddings: NDArray[np.float64], params: Dict[str, Any]
    ) -> Tuple[NDArray[np.int64], Any]:
        """Apply OPTICS clustering.

        Args:
            embeddings: 2D embeddings (n_samples, 2)
            params: OPTICS parameters

        Returns:
            Tuple of (cluster_labels, clusterer_object)
        """
        full_params = {**self.default_params(), **params}

        # Handle infinity for max_eps - can be None from UI
        max_eps = full_params["max_eps"]
        if max_eps is None or max_eps == 0 or max_eps > 1e10:
            max_eps = float("inf")

        clusterer = OPTICS(
            min_samples=full_params["min_samples"],
            xi=full_params["xi"],
            min_cluster_size=full_params["min_cluster_size"],
            max_eps=max_eps,
            cluster_method=full_params["cluster_method"],
            metric=full_params["metric"],
            p=full_params["p"],
            algorithm=full_params["algorithm"],
        )
        clusterer.fit(embeddings)
        labels = clusterer.labels_
        return labels, clusterer
