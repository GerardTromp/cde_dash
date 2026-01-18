# API Reference

This document provides reference documentation for the key APIs in the application.

## MethodRegistry

Central registry for analysis methods.

### Class: MethodRegistry

**Location**: `utils/methods/registry.py`

```python
from utils.methods import MethodRegistry
```

#### Methods

##### register_dim_reduction(method_class)

Decorator to register a dimension reduction method.

```python
@MethodRegistry.register_dim_reduction
class MyMethod:
    ...
```

##### register_clustering(method_class)

Decorator to register a clustering method.

```python
@MethodRegistry.register_clustering
class MyClustering:
    ...
```

##### get_dim_reduction(method_id: str) -> Type

Get a dimension reduction method class by ID.

```python
method_class = MethodRegistry.get_dim_reduction("umap")
instance = method_class()
```

**Raises**: `KeyError` if method not found.

##### get_clustering(method_id: str) -> Type

Get a clustering method class by ID.

```python
method_class = MethodRegistry.get_clustering("hdbscan")
instance = method_class()
```

**Raises**: `KeyError` if method not found.

##### list_dim_reduction() -> Dict[str, str]

List all registered dimension reduction methods.

```python
methods = MethodRegistry.list_dim_reduction()
# {'umap': 'UMAP', 'tsne': 't-SNE', 'pca': 'PCA'}
```

**Returns**: Dictionary mapping method_id to display name.

##### list_clustering() -> Dict[str, str]

List all registered clustering methods.

```python
methods = MethodRegistry.list_clustering()
# {'hdbscan': 'HDBSCAN', 'dbscan': 'DBSCAN', ...}
```

## Dimension Reduction Protocol

All dimension reduction methods must implement this protocol.

### Protocol: DimReductionMethod

**Location**: `utils/methods/base.py`

```python
from utils.methods.base import DimReductionMethod
```

#### Required Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Display name (e.g., "UMAP") |
| `method_id` | `str` | Unique identifier (e.g., "umap") |

#### Required Methods

##### default_params() -> Dict[str, Any]

Return default parameters for the method.

```python
@staticmethod
def default_params() -> Dict[str, Any]:
    return {
        "n_neighbors": 15,
        "min_dist": 0.1,
        "n_components": 2,
        "random_state": 42,
    }
```

##### param_schema() -> Dict[str, Dict[str, Any]]

Return parameter schema for UI generation.

```python
@staticmethod
def param_schema() -> Dict[str, Dict[str, Any]]:
    return {
        "n_neighbors": {
            "type": "int",
            "default": 15,
            "min": 2,
            "max": 200,
            "description": "Number of neighbors"
        }
    }
```

##### fit_transform(embeddings, params) -> NDArray

Apply dimension reduction.

```python
def fit_transform(
    self,
    embeddings: NDArray[np.float64],
    params: Dict[str, Any]
) -> NDArray[np.float64]:
    ...
```

**Parameters**:
- `embeddings`: Input array of shape `(n_samples, n_features)`
- `params`: Parameter dictionary

**Returns**: Array of shape `(n_samples, 2)`

## Clustering Protocol

All clustering methods must implement this protocol.

### Protocol: ClusteringMethod

**Location**: `utils/methods/base.py`

```python
from utils.methods.base import ClusteringMethod
```

#### Required Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `name` | `str` | Display name (e.g., "HDBSCAN") |
| `method_id` | `str` | Unique identifier (e.g., "hdbscan") |

#### Required Methods

##### default_params() -> Dict[str, Any]

Return default parameters for the method.

##### param_schema() -> Dict[str, Dict[str, Any]]

Return parameter schema for UI generation.

##### fit_predict(embeddings, params) -> Tuple[NDArray, Any]

Apply clustering.

```python
def fit_predict(
    self,
    embeddings: NDArray[np.float64],
    params: Dict[str, Any]
) -> Tuple[NDArray[np.int64], Any]:
    ...
```

**Parameters**:
- `embeddings`: Input array of shape `(n_samples, 2)`
- `params`: Parameter dictionary

**Returns**: Tuple of:
- `labels`: Array of cluster labels, shape `(n_samples,)`
- `clusterer`: The fitted clusterer object

## Analysis Functions

### run_analysis_single()

**Location**: `utils/run_analysis.py`

Run analysis with selected methods using the registry.

```python
def run_analysis_single(
    self,
    model_name: str,
    dim_reduction_method: str = "umap",
    clustering_method: str = "hdbscan",
) -> Optional[Dict[str, Any]]:
    ...
```

**Parameters**:
- `model_name`: Embedding model name
- `dim_reduction_method`: Method ID for dimension reduction
- `clustering_method`: Method ID for clustering

**Returns**: Dictionary with:
- `model_name`: str
- `dim_reduction_method`: str
- `dim_reduction_name`: str
- `clustering_method`: str
- `clustering_name`: str
- `filtered_cdes`: DataFrame
- `original_embeddings`: NDArray
- `visualization_embeddings`: NDArray
- `cluster_labels`: NDArray
- `clusterer`: Any
- `metrics`: Dict

### create_single_plot()

**Location**: `utils/run_analysis.py`

Create a single plot from analysis results.

```python
def create_single_plot(self, results: Dict[str, Any]) -> go.Figure:
    ...
```

### create_comparison_plot()

**Location**: `utils/run_analysis.py`

Create side-by-side comparison of two dimension reduction methods.

```python
def create_comparison_plot(
    self,
    results1: Dict[str, Any],
    results2: Dict[str, Any]
) -> go.Figure:
    ...
```

## Parameter Export

### export_params_yaml()

**Location**: `utils/export_params.py`

Export parameters to a timestamped YAML file.

```python
def export_params_yaml(
    dim_method: str,
    dim_params: Dict[str, Any],
    cluster_method: str,
    cluster_params: Dict[str, Any],
    output_dir: str = ".",
    model_name: Optional[str] = None,
) -> str:
    ...
```

**Parameters**:
- `dim_method`: Dimension reduction method ID
- `dim_params`: Dimension reduction parameters
- `cluster_method`: Clustering method ID
- `cluster_params`: Clustering parameters
- `output_dir`: Output directory (default: current)
- `model_name`: Optional model name

**Returns**: Path to created YAML file

## UI Functions

### param_inputs_from_schema()

**Location**: `utils/dash_app_functions.py`

Generate parameter inputs from a method's schema.

```python
def param_inputs_from_schema(
    schema: Dict[str, Dict[str, Any]],
    method_id: str,
    current_params: Dict[str, Any]
) -> dbc.Card:
    ...
```

### auto_cast()

**Location**: `utils/dash_app_functions.py`

Convert string input to appropriate Python type.

```python
def auto_cast(val) -> Any:
    ...
```

Handles: `int`, `float`, `bool`, `None`, `tuple`, `list`
