# Parameter Tuning

This guide covers how to tune parameters for optimal clustering results.

## Parameter Interface

When you select a method, its parameters appear in the card below the dropdown:

- **Numeric parameters**: Input fields with min/max constraints
- **Select parameters**: Dropdown menus
- **Boolean parameters**: Toggle switches

Changes are automatically saved when you modify any field.

## Understanding Metrics

The plot title displays key metrics:

```
UMAP + HDBSCAN | Clusters: 12 | Silhouette: 0.432
```

### Silhouette Score

- **Range**: -1 to 1
- **Higher is better**
- **> 0.5**: Strong cluster structure
- **0.25-0.5**: Reasonable structure
- **< 0.25**: Weak or overlapping clusters

### Number of Clusters

- HDBSCAN/DBSCAN find clusters automatically
- K-Means/Spectral use your specified count
- Noise points (cluster -1) are not counted

## Tuning Strategies

### For UMAP

**Problem**: Clusters too spread out

```
↑ Increase n_neighbors (try 30-50)
↓ Decrease min_dist (try 0.05-0.1)
```

**Problem**: Clusters too compressed

```
↓ Decrease n_neighbors (try 5-10)
↑ Increase min_dist (try 0.3-0.5)
```

### For t-SNE

**Problem**: Clusters overlap or look random

```
↓ Decrease perplexity (try 10-20)
↑ Increase max_iter (try 2000-5000)
```

**Problem**: Too many tiny clusters

```
↑ Increase perplexity (try 40-50)
```

### For HDBSCAN

**Problem**: Too many noise points

```
↓ Decrease min_cluster_size (try 5-10)
↓ Decrease min_samples (try 2-3)
```

**Problem**: Everything in one cluster

```
↑ Increase min_cluster_size (try 25-50)
```

**Problem**: Too many small clusters

```
↑ Increase min_cluster_size
→ Change cluster_selection_method to "leaf"
```

### For K-Means

**Finding optimal n_clusters**:

1. Run with different values (4, 6, 8, 10, 12)
2. Compare silhouette scores
3. Look for "elbow" - where adding clusters stops helping

### For DBSCAN

**Estimating eps**:

1. Start with eps = 0.3-0.5 for normalized data
2. If all points are noise → increase eps
3. If one giant cluster → decrease eps

## Parameter Presets

### Conservative (fewer clusters)

```yaml
HDBSCAN:
  min_cluster_size: 25
  min_samples: 10
  cluster_selection_method: leaf
```

### Aggressive (more clusters)

```yaml
HDBSCAN:
  min_cluster_size: 5
  min_samples: 2
  cluster_selection_method: eom
```

### Balanced

```yaml
HDBSCAN:
  min_cluster_size: 15
  min_samples: 5
  cluster_selection_method: eom
```

## Saving Parameters

Click **Export Parameters (YAML)** to save your current configuration.

The file includes:

- Timestamp
- Model name
- All dimension reduction parameters
- All clustering parameters

Use these files to:

- Reproduce analyses
- Share configurations
- Track parameter experiments

## Common Issues

### "Only 1 cluster found"

- Dimension reduction produced points too close together
- Try increasing n_neighbors (UMAP) or perplexity (t-SNE)
- Check if data has natural clusters

### "Too many noise points"

- HDBSCAN min_cluster_size too high
- DBSCAN eps too small
- Try PCA first to understand variance

### "Silhouette score negative"

- Clusters overlap significantly
- Try different dimension reduction settings
- Consider if data has clear cluster structure

### "Analysis too slow"

- t-SNE: Switch to barnes_hut method
- UMAP: Reduce n_neighbors
- Use PCA for initial exploration
