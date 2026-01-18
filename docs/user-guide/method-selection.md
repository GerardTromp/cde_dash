# Method Selection

Choosing the right dimension reduction and clustering methods depends on your analysis goals.

## Dimension Reduction Methods

### UMAP (Uniform Manifold Approximation and Projection)

**Best for**: Exploring global structure while preserving local relationships

**Key Parameters**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| n_neighbors | 15 | Size of local neighborhood |
| min_dist | 0.1 | Minimum distance between points |
| metric | cosine | Distance metric |

**Recommendations**:

- **Larger n_neighbors** (30-50): Emphasizes global structure
- **Smaller n_neighbors** (5-15): Emphasizes local clusters
- **Smaller min_dist** (0.0-0.1): Tighter clusters
- **Larger min_dist** (0.5-1.0): More spread out

### t-SNE (t-Distributed Stochastic Neighbor Embedding)

**Best for**: Visualizing local cluster structure, finding tight groups

**Key Parameters**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| perplexity | 30 | Balance local/global aspects |
| metric | cosine | Distance metric |
| method | exact | Computation method |
| max_iter | 1000 | Optimization iterations |

**Recommendations**:

- **Perplexity** should be between 5 and 50
- Rule of thumb: perplexity ≈ sqrt(n_samples)
- Use **barnes_hut** method for datasets > 1000 points
- Increase **max_iter** if clusters aren't well-separated

### PCA (Principal Component Analysis)

**Best for**: Quick overview, understanding variance structure

**Key Parameters**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| whiten | False | Normalize to unit variance |
| svd_solver | auto | Algorithm selection |

**Recommendations**:

- Use for initial exploration before UMAP/t-SNE
- Enable **whiten** for more uniform scaling
- Fast enough for very large datasets

## Clustering Methods

### HDBSCAN (Hierarchical DBSCAN)

**Best for**: Finding natural clusters of varying density without specifying cluster count

**Key Parameters**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| min_cluster_size | 15 | Minimum points per cluster |
| min_samples | 5 | Core point threshold |
| metric | euclidean | Distance metric |
| cluster_selection_method | eom | Cluster extraction method |

**Recommendations**:

- Start with **min_cluster_size** = 5-15
- Increase if too many small clusters
- **eom** (Excess of Mass) finds smaller clusters
- **leaf** finds larger, more stable clusters

### DBSCAN

**Best for**: Simple density-based clustering with fixed neighborhood size

**Key Parameters**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| eps | 0.5 | Neighborhood radius |
| min_samples | 5 | Core point threshold |
| metric | euclidean | Distance metric |

**Recommendations**:

- **eps** is critical - too small = all noise, too large = one cluster
- Use a k-distance plot to estimate eps
- More sensitive to parameter choice than HDBSCAN

### K-Means

**Best for**: When you know the number of clusters you want

**Key Parameters**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| n_clusters | 8 | Number of clusters |
| init | k-means++ | Initialization method |
| n_init | 10 | Number of restarts |

**Recommendations**:

- Use elbow method or silhouette analysis to choose n_clusters
- **k-means++** initialization is more stable
- Does NOT handle noise points

### Spectral Clustering

**Best for**: Non-convex cluster shapes, graph-based relationships

**Key Parameters**:

| Parameter | Default | Description |
|-----------|---------|-------------|
| n_clusters | 8 | Number of clusters |
| affinity | rbf | Similarity metric |
| n_neighbors | 10 | For 'nearest_neighbors' affinity |

**Recommendations**:

- Use **rbf** (radial basis function) for smooth clusters
- Use **nearest_neighbors** for graph-based structure
- Slower than K-Means but finds complex shapes

## Method Combinations

### Recommended Combinations

| Goal | Dim Reduction | Clustering |
|------|--------------|------------|
| Exploratory analysis | UMAP | HDBSCAN |
| Fine-grained clusters | t-SNE | HDBSCAN |
| Known cluster count | PCA or UMAP | K-Means |
| Complex shapes | UMAP | Spectral |

### Comparison Mode

Use comparison mode to evaluate:

- UMAP vs t-SNE with same clustering
- Different parameter settings

This helps validate that clusters are real and not artifacts of the method.
