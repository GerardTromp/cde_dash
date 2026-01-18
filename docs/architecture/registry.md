# Method Registry

The Method Registry is the core of the plugin architecture, enabling dynamic method registration and discovery.

## Overview

The registry provides:

- Decorator-based method registration
- Method lookup by ID
- Method enumeration for UI generation
- Type-safe method interfaces

## Registry Implementation

**Location**: `utils/methods/registry.py`

```python
class MethodRegistry:
    """Central registry for all analysis methods."""

    _dim_reduction: Dict[str, Type] = {}
    _clustering: Dict[str, Type] = {}

    @classmethod
    def register_dim_reduction(cls, method_class: Type) -> Type:
        """Decorator to register a dimension reduction method."""
        cls._dim_reduction[method_class.method_id] = method_class
        return method_class

    @classmethod
    def register_clustering(cls, method_class: Type) -> Type:
        """Decorator to register a clustering method."""
        cls._clustering[method_class.method_id] = method_class
        return method_class

    @classmethod
    def get_dim_reduction(cls, method_id: str) -> Type:
        """Get dimension reduction method by ID."""
        return cls._dim_reduction[method_id]

    @classmethod
    def get_clustering(cls, method_id: str) -> Type:
        """Get clustering method by ID."""
        return cls._clustering[method_id]

    @classmethod
    def list_dim_reduction(cls) -> Dict[str, str]:
        """List all registered dimension reduction methods."""
        return {mid: m.name for mid, m in cls._dim_reduction.items()}

    @classmethod
    def list_clustering(cls) -> Dict[str, str]:
        """List all registered clustering methods."""
        return {mid: m.name for mid, m in cls._clustering.items()}
```

## Protocol Definitions

**Location**: `utils/methods/base.py`

### Dimension Reduction Protocol

```python
@runtime_checkable
class DimReductionMethod(Protocol):
    """Protocol for dimension reduction methods."""

    name: str           # Display name (e.g., "UMAP")
    method_id: str      # Registry key (e.g., "umap")

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default parameters."""
        ...

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        ...

    def fit_transform(
        self,
        embeddings: NDArray[np.float64],
        params: Dict[str, Any]
    ) -> NDArray[np.float64]:
        """Apply dimension reduction."""
        ...
```

### Clustering Protocol

```python
@runtime_checkable
class ClusteringMethod(Protocol):
    """Protocol for clustering methods."""

    name: str
    method_id: str

    @staticmethod
    def default_params() -> Dict[str, Any]: ...

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]: ...

    def fit_predict(
        self,
        embeddings: NDArray[np.float64],
        params: Dict[str, Any]
    ) -> Tuple[NDArray[np.int64], Any]:
        """Apply clustering. Returns (labels, clusterer)."""
        ...
```

## Registration Flow

```
1. Import triggers module loading
   └─> from utils.methods import MethodRegistry

2. Submodules imported
   └─> from .dim_reduction import *
   └─> from .clustering import *

3. Decorator executes on class definition
   └─> @MethodRegistry.register_dim_reduction
   └─> class UMAPMethod: ...

4. Method stored in registry dict
   └─> _dim_reduction["umap"] = UMAPMethod
```

## Usage Examples

### Registering a Method

```python
from utils.methods import MethodRegistry

@MethodRegistry.register_dim_reduction
class MyMethod:
    name = "My Custom Method"
    method_id = "my_method"

    @staticmethod
    def default_params():
        return {"param1": 10}

    @staticmethod
    def param_schema():
        return {
            "param1": {
                "type": "int",
                "default": 10,
                "min": 1,
                "max": 100
            }
        }

    def fit_transform(self, embeddings, params):
        # Implementation
        pass
```

### Looking Up a Method

```python
from utils.methods import MethodRegistry

# Get method class
method_class = MethodRegistry.get_dim_reduction("umap")

# Get default parameters
defaults = method_class.default_params()

# Create instance and use
method = method_class()
result = method.fit_transform(embeddings, params)
```

### Enumerating Methods

```python
from utils.methods import MethodRegistry

# For UI dropdown
dim_methods = MethodRegistry.list_dim_reduction()
# {'umap': 'UMAP', 'tsne': 't-SNE', 'pca': 'PCA'}

cluster_methods = MethodRegistry.list_clustering()
# {'hdbscan': 'HDBSCAN', 'dbscan': 'DBSCAN', ...}
```

## Import Structure

The package uses a layered import structure:

```python
# utils/methods/__init__.py
from .registry import MethodRegistry

# Import submodules to trigger registration
from .dim_reduction import *  # noqa: F401, F403
from .clustering import *     # noqa: F401, F403

__all__ = ["MethodRegistry"]
```

This ensures all methods are registered when the package is imported.

## Thread Safety

The registry uses class-level dictionaries which are not thread-safe for writes. However:

- Registration happens at import time (single-threaded)
- Runtime access is read-only (thread-safe)
- No dynamic registration after startup

## See Also

- [Plugin System](plugins.md): How to add new methods
- [API Reference](../api/registry.md): Full API documentation
