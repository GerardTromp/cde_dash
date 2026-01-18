# Clustering Methods

## Available Methods

| Method | ID | Description | Finds # Clusters |
|--------|-----|-------------|-----------------|
| HDBSCAN | `hdbscan` | Hierarchical Density-Based Clustering | Automatic |
| DBSCAN | `dbscan` | Density-Based Spatial Clustering | Automatic |
| K-Means | `kmeans` | Centroid-based partitioning | User-specified |
| Spectral | `spectral` | Graph-based clustering | User-specified |

## HDBSCAN

**Class**: `HDBSCANMethod`
**Location**: `utils/methods/clustering/hdbscan.py`

### Default Parameters

```python
{
    "min_cluster_size": 15,
    "min_samples": 5,
    "metric": "euclidean",
    "cluster_selection_method": "eom",
}
```

### Parameter Schema

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| min_cluster_size | int | 15 | 2-100 | Minimum points per cluster |
| min_samples | int | 5 | 1-50 | Core point threshold |
| metric | select | euclidean | euclidean, manhattan | Distance metric |
| cluster_selection_method | select | eom | eom, leaf | Cluster extraction method |

### Usage

```python
from utils.methods import MethodRegistry

method = MethodRegistry.get_clustering("hdbscan")()
labels, clusterer = method.fit_predict(embeddings_2d, {"min_cluster_size": 10})
```

### Notes

- Automatically determines number of clusters
- Noise points are labeled as -1
- `eom` finds smaller clusters, `leaf` finds larger ones

---

## DBSCAN

**Class**: `DBSCANMethod`
**Location**: `utils/methods/clustering/dbscan.py`

### Default Parameters

```python
{
    "eps": 0.5,
    "min_samples": 5,
    "metric": "euclidean",
}
```

### Parameter Schema

| Parameter | Type | Default | Range | Description |
|-----------|------|---------|-------|-------------|
| eps | float | 0.5 | 0.01-2.0 | Neighborhood radius |
| min_samples | int | 5 | 1-50 | Minimum points in neighborhood |
| metric | select | euclidean | euclidean, manhattan, cosine | Distance metric |

### Usage

```python
from utils.methods import MethodRegistry

method = MethodRegistry.get_clustering("dbscan")()
labels, clusterer = method.fit_predict(embeddings_2d, {"eps": 0.3})
```

### Notes

- `eps` is critical - too small = all noise, too large = one cluster
- More sensitive to parameter choice than HDBSCAN

---

## K-Means

**Class**: `KMeansMethod`
**Location**: `utils/methods/clustering/kmeans.py`

### Default Parameters

```python
{
    "n_clusters": 8,
    "init": "k-means++",
    "n_init": 10,
    "random_state": 42,
}
```

### Parameter Schema

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| n_clusters | int | 8 | 2-50 | Number of clusters |
| init | select | k-means++ | k-means++, random | Initialization method |
| n_init | int | 10 | 1-20 | Number of initializations |

### Usage

```python
from utils.methods import MethodRegistry

method = MethodRegistry.get_clustering("kmeans")()
labels, clusterer = method.fit_predict(embeddings_2d, {"n_clusters": 10})
```

### Notes

- Requires specifying number of clusters
- Does NOT identify noise points
- All points are assigned to a cluster

---

## Spectral

**Class**: `SpectralMethod`
**Location**: `utils/methods/clustering/spectral.py`

### Default Parameters

```python
{
    "n_clusters": 8,
    "affinity": "rbf",
    "n_neighbors": 10,
    "random_state": 42,
}
```

### Parameter Schema

| Parameter | Type | Default | Range/Options | Description |
|-----------|------|---------|---------------|-------------|
| n_clusters | int | 8 | 2-50 | Number of clusters |
| affinity | select | rbf | rbf, nearest_neighbors | Affinity matrix type |
| n_neighbors | int | 10 | 2-50 | For nearest_neighbors affinity |

### Usage

```python
from utils.methods import MethodRegistry

method = MethodRegistry.get_clustering("spectral")()
labels, clusterer = method.fit_predict(embeddings_2d, {"n_clusters": 6})
```

### Notes

- Good for non-convex cluster shapes
- Requires specifying number of clusters
- Slower than K-Means

---

## Protocol: ClusteringMethod

All clustering methods implement this protocol:

```python
@runtime_checkable
class ClusteringMethod(Protocol):
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
    ) -> Tuple[NDArray[np.int64], Any]: ...
```

### fit_predict

**Parameters**:
- `embeddings`: 2D array of shape `(n_samples, 2)`
- `params`: Dictionary of parameters (merged with defaults)

**Returns**: Tuple of:
- `labels`: Array of cluster labels, shape `(n_samples,)`. Label -1 indicates noise.
- `clusterer`: The fitted clusterer object (for inspection)

---

## Choosing a Method

| Use Case | Recommended Method |
|----------|-------------------|
| Unknown number of clusters | HDBSCAN |
| Simple density-based | DBSCAN |
| Known number of clusters | K-Means |
| Non-convex shapes | Spectral |
| Handle noise | HDBSCAN or DBSCAN |
| Speed priority | K-Means |
