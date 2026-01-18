# Plugin System

The plugin system allows adding new dimension reduction and clustering methods without modifying core application code.

## Architecture

```
utils/methods/
├── __init__.py              # Registry export + submodule imports
├── base.py                  # Protocol definitions
├── registry.py              # MethodRegistry class
├── dim_reduction/
│   ├── __init__.py          # Import all methods
│   ├── umap_method.py       # UMAP plugin
│   ├── tsne.py              # t-SNE plugin
│   └── pca.py               # PCA plugin
└── clustering/
    ├── __init__.py          # Import all methods
    ├── hdbscan.py           # HDBSCAN plugin
    ├── dbscan.py            # DBSCAN plugin
    ├── kmeans.py            # K-Means plugin
    └── spectral.py          # Spectral plugin
```

## Adding a New Dimension Reduction Method

### Step 1: Create the Plugin File

Create `utils/methods/dim_reduction/my_method.py`:

```python
"""My custom dimension reduction method."""

from typing import Dict, Any
import numpy as np
from numpy.typing import NDArray
from sklearn.preprocessing import StandardScaler

from ..registry import MethodRegistry


@MethodRegistry.register_dim_reduction
class MyMethod:
    """My custom dimension reduction implementation."""

    # Required class attributes
    name = "My Method"        # Display name in UI
    method_id = "my_method"   # Unique identifier (used in registry)

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default parameters.

        These are used when no parameters are provided.
        """
        return {
            "param1": 10,
            "param2": 0.5,
            "n_components": 2,      # Usually fixed at 2 for visualization
            "random_state": 42,     # For reproducibility
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation.

        Only include parameters that should be user-configurable.
        """
        return {
            "param1": {
                "type": "int",
                "default": 10,
                "min": 1,
                "max": 100,
                "step": 1,
                "description": "Description of param1",
            },
            "param2": {
                "type": "float",
                "default": 0.5,
                "min": 0.0,
                "max": 1.0,
                "step": 0.1,
                "description": "Description of param2",
            },
        }

    def fit_transform(
        self,
        embeddings: NDArray[np.float64],
        params: Dict[str, Any]
    ) -> NDArray[np.float64]:
        """Apply dimension reduction.

        Args:
            embeddings: High-dimensional embeddings (n_samples, n_features)
            params: Parameters from UI or defaults

        Returns:
            2D embeddings (n_samples, 2)
        """
        # Merge with defaults
        full_params = {**self.default_params(), **params}

        # Preprocessing (recommended)
        scaler = StandardScaler()
        scaled = scaler.fit_transform(embeddings)

        # Your implementation
        # result = my_algorithm(scaled, **full_params)

        return result
```

### Step 2: Register in __init__.py

Edit `utils/methods/dim_reduction/__init__.py`:

```python
from .umap_method import UMAPMethod
from .tsne import TSNEMethod
from .pca import PCAMethod
from .my_method import MyMethod  # Add this line

__all__ = ["UMAPMethod", "TSNEMethod", "PCAMethod", "MyMethod"]
```

### Step 3: Test the Plugin

```python
from utils.methods import MethodRegistry

# Verify registration
print(MethodRegistry.list_dim_reduction())
# Should include: {'my_method': 'My Method', ...}

# Test execution
method = MethodRegistry.get_dim_reduction("my_method")()
result = method.fit_transform(test_embeddings, {})
print(f"Output shape: {result.shape}")
```

## Adding a New Clustering Method

### Step 1: Create the Plugin File

Create `utils/methods/clustering/my_clustering.py`:

```python
"""My custom clustering method."""

from typing import Dict, Any, Tuple
import numpy as np
from numpy.typing import NDArray

from ..registry import MethodRegistry


@MethodRegistry.register_clustering
class MyClustering:
    """My custom clustering implementation."""

    name = "My Clustering"
    method_id = "my_clustering"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        return {
            "n_clusters": 8,
            "param1": 10,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        return {
            "n_clusters": {
                "type": "int",
                "default": 8,
                "min": 2,
                "max": 50,
                "description": "Number of clusters",
            },
            "param1": {
                "type": "int",
                "default": 10,
                "min": 1,
                "max": 100,
                "description": "Description of param1",
            },
        }

    def fit_predict(
        self,
        embeddings: NDArray[np.float64],
        params: Dict[str, Any]
    ) -> Tuple[NDArray[np.int64], Any]:
        """Apply clustering.

        Args:
            embeddings: 2D reduced embeddings (n_samples, 2)
            params: Parameters from UI or defaults

        Returns:
            Tuple of (cluster_labels, clusterer_object)
            - cluster_labels: Array of cluster assignments (-1 for noise)
            - clusterer_object: The fitted clusterer (for inspection)
        """
        full_params = {**self.default_params(), **params}

        # Your implementation
        # clusterer = MyAlgorithm(**full_params)
        # clusterer.fit(embeddings)
        # labels = clusterer.labels_

        return labels, clusterer
```

### Step 2: Register in __init__.py

Edit `utils/methods/clustering/__init__.py`:

```python
from .hdbscan import HDBSCANMethod
from .dbscan import DBSCANMethod
from .kmeans import KMeansMethod
from .spectral import SpectralMethod
from .my_clustering import MyClustering  # Add this line

__all__ = ["HDBSCANMethod", "DBSCANMethod", "KMeansMethod",
           "SpectralMethod", "MyClustering"]
```

## Parameter Schema Reference

### Type: int

```python
"param_name": {
    "type": "int",
    "default": 10,
    "min": 1,       # Optional
    "max": 100,     # Optional
    "step": 1,      # Optional, default 1
    "description": "Parameter description"
}
```

### Type: float

```python
"param_name": {
    "type": "float",
    "default": 0.5,
    "min": 0.0,     # Optional
    "max": 1.0,     # Optional
    "step": 0.01,   # Optional, default 0.01
    "description": "Parameter description"
}
```

### Type: bool

```python
"param_name": {
    "type": "bool",
    "default": False,
    "description": "Parameter description"
}
```

### Type: select

```python
"param_name": {
    "type": "select",
    "default": "option1",
    "options": ["option1", "option2", "option3"],
    "description": "Parameter description"
}
```

## Best Practices

### 1. Always Use StandardScaler

```python
from sklearn.preprocessing import StandardScaler

scaler = StandardScaler()
scaled = scaler.fit_transform(embeddings)
```

### 2. Handle Edge Cases

```python
# Adjust parameters based on data size
if full_params["param1"] > len(embeddings) // 2:
    full_params["param1"] = max(2, len(embeddings) // 2)
```

### 3. Set Random State

```python
def default_params():
    return {
        ...
        "random_state": 42,  # For reproducibility
    }
```

### 4. Include Useful Defaults

Choose defaults that work for typical use cases (hundreds to thousands of samples).

### 5. Document Parameters

Use the `description` field to help users understand each parameter.

## Testing

### Basic Functionality Test

```python
import numpy as np
from utils.methods import MethodRegistry

# Generate test data
test_data = np.random.randn(100, 50)

# Test dimension reduction
for method_id in MethodRegistry.list_dim_reduction():
    method = MethodRegistry.get_dim_reduction(method_id)()
    result = method.fit_transform(test_data, {})
    assert result.shape == (100, 2)
    print(f"{method_id}: OK")

# Test clustering
test_2d = np.random.randn(100, 2)
for method_id in MethodRegistry.list_clustering():
    method = MethodRegistry.get_clustering(method_id)()
    labels, _ = method.fit_predict(test_2d, {})
    assert len(labels) == 100
    print(f"{method_id}: OK")
```
