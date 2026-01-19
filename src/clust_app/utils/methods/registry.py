"""Central registry for all analysis methods."""

from typing import Dict, Type, Any


class MethodRegistry:
    """Central registry for dimension reduction and clustering methods.

    Methods register themselves using decorators:
        @MethodRegistry.register_dim_reduction
        class MyMethod:
            ...
    """

    _dim_reduction: Dict[str, Type] = {}
    _clustering: Dict[str, Type] = {}

    @classmethod
    def register_dim_reduction(cls, method_class: Type) -> Type:
        """Register a dimension reduction method."""
        cls._dim_reduction[method_class.method_id] = method_class
        return method_class

    @classmethod
    def register_clustering(cls, method_class: Type) -> Type:
        """Register a clustering method."""
        cls._clustering[method_class.method_id] = method_class
        return method_class

    @classmethod
    def get_dim_reduction(cls, method_id: str) -> Type:
        """Get a dimension reduction method class by ID."""
        if method_id not in cls._dim_reduction:
            raise KeyError(
                f"Unknown dimension reduction method: {method_id}. "
                f"Available: {list(cls._dim_reduction.keys())}"
            )
        return cls._dim_reduction[method_id]

    @classmethod
    def get_clustering(cls, method_id: str) -> Type:
        """Get a clustering method class by ID."""
        if method_id not in cls._clustering:
            raise KeyError(
                f"Unknown clustering method: {method_id}. "
                f"Available: {list(cls._clustering.keys())}"
            )
        return cls._clustering[method_id]

    @classmethod
    def list_dim_reduction(cls) -> Dict[str, str]:
        """Return dict of {method_id: display_name} for dim reduction methods."""
        return {mid: m.name for mid, m in cls._dim_reduction.items()}

    @classmethod
    def list_clustering(cls) -> Dict[str, str]:
        """Return dict of {method_id: display_name} for clustering methods."""
        return {mid: m.name for mid, m in cls._clustering.items()}

    @classmethod
    def get_dim_reduction_defaults(cls, method_id: str) -> Dict[str, Any]:
        """Get default parameters for a dimension reduction method."""
        return cls.get_dim_reduction(method_id).default_params()

    @classmethod
    def get_clustering_defaults(cls, method_id: str) -> Dict[str, Any]:
        """Get default parameters for a clustering method."""
        return cls.get_clustering(method_id).default_params()
