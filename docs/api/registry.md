# MethodRegistry API

## Overview

The `MethodRegistry` class provides centralized registration and discovery for analysis methods.

## Import

```python
from utils.methods import MethodRegistry
```

## Class Methods

### register_dim_reduction

```python
@classmethod
def register_dim_reduction(cls, method_class: Type) -> Type
```

Decorator to register a dimension reduction method.

**Example**:
```python
@MethodRegistry.register_dim_reduction
class UMAPMethod:
    name = "UMAP"
    method_id = "umap"
    ...
```

---

### register_clustering

```python
@classmethod
def register_clustering(cls, method_class: Type) -> Type
```

Decorator to register a clustering method.

**Example**:
```python
@MethodRegistry.register_clustering
class HDBSCANMethod:
    name = "HDBSCAN"
    method_id = "hdbscan"
    ...
```

---

### get_dim_reduction

```python
@classmethod
def get_dim_reduction(cls, method_id: str) -> Type
```

Retrieve a dimension reduction method class by its ID.

**Parameters**:
- `method_id`: The unique identifier of the method (e.g., "umap")

**Returns**: The method class

**Raises**: `KeyError` if method not found

**Example**:
```python
method_class = MethodRegistry.get_dim_reduction("umap")
method = method_class()
result = method.fit_transform(embeddings, params)
```

---

### get_clustering

```python
@classmethod
def get_clustering(cls, method_id: str) -> Type
```

Retrieve a clustering method class by its ID.

**Parameters**:
- `method_id`: The unique identifier of the method (e.g., "hdbscan")

**Returns**: The method class

**Raises**: `KeyError` if method not found

---

### list_dim_reduction

```python
@classmethod
def list_dim_reduction(cls) -> Dict[str, str]
```

List all registered dimension reduction methods.

**Returns**: Dictionary mapping method_id to display name

**Example**:
```python
methods = MethodRegistry.list_dim_reduction()
# {'umap': 'UMAP', 'tsne': 't-SNE', 'pca': 'PCA'}

for method_id, name in methods.items():
    print(f"{method_id}: {name}")
```

---

### list_clustering

```python
@classmethod
def list_clustering(cls) -> Dict[str, str]
```

List all registered clustering methods.

**Returns**: Dictionary mapping method_id to display name

## Usage Patterns

### Creating UI Dropdowns

```python
from utils.methods import MethodRegistry

# Build options for Dash dropdown
dim_options = [
    {"label": name, "value": mid}
    for mid, name in MethodRegistry.list_dim_reduction().items()
]
```

### Running Analysis

```python
from utils.methods import MethodRegistry

# Get methods
dim_class = MethodRegistry.get_dim_reduction("umap")
cluster_class = MethodRegistry.get_clustering("hdbscan")

# Get parameters
dim_params = dim_class.default_params()
cluster_params = cluster_class.default_params()

# Run dimension reduction
dim_reducer = dim_class()
vis_embeddings = dim_reducer.fit_transform(embeddings, dim_params)

# Run clustering
clusterer = cluster_class()
labels, model = clusterer.fit_predict(vis_embeddings, cluster_params)
```

### Checking Available Methods

```python
from utils.methods import MethodRegistry

print("Dimension Reduction Methods:")
for mid, name in MethodRegistry.list_dim_reduction().items():
    method = MethodRegistry.get_dim_reduction(mid)
    print(f"  {name} ({mid})")
    print(f"    Params: {list(method.param_schema().keys())}")

print("\nClustering Methods:")
for mid, name in MethodRegistry.list_clustering().items():
    method = MethodRegistry.get_clustering(mid)
    print(f"  {name} ({mid})")
    print(f"    Params: {list(method.param_schema().keys())}")
```
