# Dimension Reduction Methods

## Available Methods

| Method | ID | Description |
|--------|-----|------------|
| UMAP | `umap` | Uniform Manifold Approximation and Projection |
| t-SNE | `tsne` | t-Distributed Stochastic Neighbor Embedding |
| PCA | `pca` | Principal Component Analysis |

## UMAP

**Class**: `UMAPMethod`
**Location**: `utils/methods/dim_reduction/umap_method.py`

### Default Parameters

```python
{
    "n_neighbors": 15,
    "min_dist": 0.1,
    "metric": "cosine",
    "n_components": 2,
    "random_state": 42,
}
```

### Parameter Schema

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| n_neighbors | int | 15 | 2-200 | Number of neighbors for manifold approximation |
| min_dist | float | 0.1 | 0.0-1.0 | Minimum distance between points |
| metric | select | cosine | cosine, euclidean, manhattan, correlation | Distance metric |

### Usage

```python
from utils.methods import MethodRegistry

method = MethodRegistry.get_dim_reduction("umap")()
result = method.fit_transform(embeddings, {"n_neighbors": 20})
```

---

## t-SNE

**Class**: `TSNEMethod`
**Location**: `utils/methods/dim_reduction/tsne.py`

### Default Parameters

```python
{
    "perplexity": 30,
    "metric": "cosine",
    "method": "exact",
    "n_components": 2,
    "random_state": 42,
    "max_iter": 1000,
}
```

### Parameter Schema

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| perplexity | int | 30 | 5-100 | Perplexity (effective number of neighbors) |
| metric | select | cosine | cosine, euclidean | Distance metric |
| method | select | exact | exact, barnes_hut | Computation method |
| max_iter | int | 1000 | 250-5000 | Maximum iterations for optimization |

### Usage

```python
from utils.methods import MethodRegistry

method = MethodRegistry.get_dim_reduction("tsne")()
result = method.fit_transform(embeddings, {"perplexity": 50})
```

### Notes

- Use `barnes_hut` method for datasets > 1000 samples
- Perplexity is automatically capped at `n_samples // 4`

---

## PCA

**Class**: `PCAMethod`
**Location**: `utils/methods/dim_reduction/pca.py`

### Default Parameters

```python
{
    "n_components": 2,
    "whiten": False,
    "svd_solver": "auto",
    "random_state": 42,
}
```

### Parameter Schema

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| whiten | bool | False | - | Normalize components to unit variance |
| svd_solver | select | auto | auto, full, arpack, randomized | SVD algorithm |

### Usage

```python
from utils.methods import MethodRegistry

method = MethodRegistry.get_dim_reduction("pca")()
result = method.fit_transform(embeddings, {"whiten": True})
```

### Notes

- PCA is the fastest method but provides a linear projection
- Good for initial exploration before trying UMAP/t-SNE
- `whiten=True` can help normalize scale

---

## Protocol: DimReductionMethod

All dimension reduction methods implement this protocol:

```python
@runtime_checkable
class DimReductionMethod(Protocol):
    name: str
    method_id: str

    @staticmethod
    def default_params() -> Dict[str, Any]: ...

    @staticmethod
    def param_schema() -> Dict[str, Dict[str, Any]]: ...

    def fit_transform(
        self,
        embeddings: NDArray[np.float64],
        params: Dict[str, Any]
    ) -> NDArray[np.float64]: ...
```

### fit_transform

**Parameters**:
- `embeddings`: Input array of shape `(n_samples, n_features)`
- `params`: Dictionary of parameters (merged with defaults)

**Returns**: Array of shape `(n_samples, 2)`

**Notes**:
- Input embeddings are typically standardized internally
- Parameters from `params` override defaults
- Edge cases (small datasets) are handled by capping parameters
