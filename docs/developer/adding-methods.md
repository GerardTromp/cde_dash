# Adding New Methods

This guide walks through adding new dimension reduction or clustering methods to the application.

## Quick Start

### Adding a Dimension Reduction Method

1. Create file: `utils/methods/dim_reduction/new_method.py`
2. Implement the method class with `@MethodRegistry.register_dim_reduction`
3. Add import to `utils/methods/dim_reduction/__init__.py`
4. Test and verify

### Adding a Clustering Method

1. Create file: `utils/methods/clustering/new_method.py`
2. Implement the method class with `@MethodRegistry.register_clustering`
3. Add import to `utils/methods/clustering/__init__.py`
4. Test and verify

## Complete Example: Adding Isomap

Let's add Isomap as a new dimension reduction method.

### Step 1: Create the File

Create `utils/methods/dim_reduction/isomap.py`:

```python
"""Isomap dimension reduction method."""

from typing import Dict, Any
import numpy as np
from numpy.typing import NDArray
from sklearn.manifold import Isomap
from sklearn.preprocessing import StandardScaler

from ..registry import MethodRegistry


@MethodRegistry.register_dim_reduction
class IsomapMethod:
    """Isomap (Isometric Mapping) dimension reduction."""

    name = "Isomap"
    method_id = "isomap"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default Isomap parameters."""
        return {
            "n_neighbors": 10,
            "n_components": 2,
            "metric": "minkowski",
            "p": 2,
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            "n_neighbors": {
                "type": "int",
                "default": 10,
                "min": 2,
                "max": 100,
                "description": "Number of neighbors for manifold approximation",
            },
            "metric": {
                "type": "select",
                "default": "minkowski",
                "options": ["minkowski", "euclidean", "manhattan"],
                "description": "Distance metric",
            },
        }

    def fit_transform(
        self,
        embeddings: NDArray[np.float64],
        params: Dict[str, Any]
    ) -> NDArray[np.float64]:
        """Apply Isomap dimension reduction.

        Args:
            embeddings: High-dimensional embeddings (n_samples, n_features)
            params: Isomap parameters

        Returns:
            2D embeddings (n_samples, 2)
        """
        full_params = {**self.default_params(), **params}

        # Adjust n_neighbors to not exceed data size
        max_neighbors = max(2, len(embeddings) - 1)
        full_params["n_neighbors"] = min(
            full_params["n_neighbors"],
            max_neighbors
        )

        # Standardize embeddings
        scaler = StandardScaler()
        scaled = scaler.fit_transform(embeddings)

        # Apply Isomap
        isomap = Isomap(
            n_neighbors=full_params["n_neighbors"],
            n_components=full_params["n_components"],
            metric=full_params["metric"],
            p=full_params.get("p", 2),
        )
        return isomap.fit_transform(scaled)
```

### Step 2: Update __init__.py

Edit `utils/methods/dim_reduction/__init__.py`:

```python
"""Dimension reduction method plugins."""

from .umap_method import UMAPMethod
from .tsne import TSNEMethod
from .pca import PCAMethod
from .isomap import IsomapMethod  # Add this

__all__ = ["UMAPMethod", "TSNEMethod", "PCAMethod", "IsomapMethod"]
```

### Step 3: Test

```python
import numpy as np
from utils.methods import MethodRegistry

# Check registration
print(MethodRegistry.list_dim_reduction())
# Should include 'isomap': 'Isomap'

# Test functionality
test_data = np.random.randn(100, 50)
method = MethodRegistry.get_dim_reduction("isomap")()
result = method.fit_transform(test_data, {})
print(f"Input: {test_data.shape}, Output: {result.shape}")
# Input: (100, 50), Output: (100, 2)
```

### Step 4: Run Application

```bash
python domains_clustering_interactive_plots_dash.py --port 8050
```

The new method should appear in the dimension reduction dropdown.

## Complete Example: Adding Agglomerative Clustering

### Step 1: Create the File

Create `utils/methods/clustering/agglomerative.py`:

```python
"""Agglomerative clustering method."""

from typing import Dict, Any, Tuple
import numpy as np
from numpy.typing import NDArray
from sklearn.cluster import AgglomerativeClustering

from ..registry import MethodRegistry


@MethodRegistry.register_clustering
class AgglomerativeMethod:
    """Agglomerative (Hierarchical) clustering."""

    name = "Agglomerative"
    method_id = "agglomerative"

    @staticmethod
    def default_params() -> Dict[str, Any]:
        """Return default agglomerative parameters."""
        return {
            "n_clusters": 8,
            "linkage": "ward",
            "metric": "euclidean",
        }

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]:
        """Return parameter schema for UI generation."""
        return {
            "n_clusters": {
                "type": "int",
                "default": 8,
                "min": 2,
                "max": 50,
                "description": "Number of clusters to find",
            },
            "linkage": {
                "type": "select",
                "default": "ward",
                "options": ["ward", "complete", "average", "single"],
                "description": "Linkage criterion",
            },
        }

    def fit_predict(
        self,
        embeddings: NDArray[np.float64],
        params: Dict[str, Any]
    ) -> Tuple[NDArray[np.int64], Any]:
        """Apply agglomerative clustering.

        Args:
            embeddings: 2D embeddings (n_samples, 2)
            params: Clustering parameters

        Returns:
            Tuple of (cluster_labels, clusterer)
        """
        full_params = {**self.default_params(), **params}

        # Ensure n_clusters doesn't exceed sample count
        full_params["n_clusters"] = min(
            full_params["n_clusters"],
            len(embeddings)
        )

        clusterer = AgglomerativeClustering(
            n_clusters=full_params["n_clusters"],
            linkage=full_params["linkage"],
        )

        labels = clusterer.fit_predict(embeddings)
        return labels.astype(np.int64), clusterer
```

### Step 2: Update __init__.py

Edit `utils/methods/clustering/__init__.py`:

```python
"""Clustering method plugins."""

from .hdbscan import HDBSCANMethod
from .dbscan import DBSCANMethod
from .kmeans import KMeansMethod
from .spectral import SpectralMethod
from .agglomerative import AgglomerativeMethod  # Add this

__all__ = [
    "HDBSCANMethod",
    "DBSCANMethod",
    "KMeansMethod",
    "SpectralMethod",
    "AgglomerativeMethod",
]
```

## Checklist

Before submitting a new method, verify:

- [ ] Class has `name` and `method_id` attributes
- [ ] `default_params()` returns all required parameters
- [ ] `param_schema()` only exposes user-configurable params
- [ ] Method handles edge cases (small datasets, extreme params)
- [ ] Random state is set for reproducibility
- [ ] StandardScaler preprocessing (for dim reduction)
- [ ] Import added to `__init__.py`
- [ ] Basic test passes
- [ ] Method appears in UI dropdown

## Troubleshooting

### Method not appearing in dropdown

1. Check import in `__init__.py`
2. Check for import errors: `python -c "from utils.methods import MethodRegistry"`
3. Verify decorator: `@MethodRegistry.register_dim_reduction`

### Parameter not showing in UI

1. Verify parameter is in `param_schema()` (not just `default_params()`)
2. Check type is valid: `int`, `float`, `bool`, `select`

### Error during analysis

1. Check `fit_transform` or `fit_predict` signature matches protocol
2. Verify return types (numpy arrays)
3. Handle edge cases in parameter values
