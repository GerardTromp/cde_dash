# Quick Start

This guide walks you through running your first clustering analysis.

## Start the Application

```bash
# Activate your environment
source venv/bin/activate

# Run with default settings
python domains_clustering_interactive_plots_dash.py

# Or specify a custom port
python domains_clustering_interactive_plots_dash.py --port 8080
```

Open your browser to [http://127.0.0.1:8050](http://127.0.0.1:8050).

## The Interface

The application presents several sections:

### 1. Embedding Model Selection

Select which precomputed embedding model to use for analysis:

- **SAPBERT**: Biomedical concept embeddings
- **MedCPT**: Medical passage retrieval embeddings

### 2. Method Selection

Choose your analysis methods:

**Dimension Reduction** (left panel):

- **UMAP** - Good for preserving global structure
- **t-SNE** - Good for preserving local neighborhoods
- **PCA** - Fast, linear reduction

**Clustering** (right panel):

- **HDBSCAN** - Density-based, finds natural clusters
- **DBSCAN** - Density-based with fixed epsilon
- **K-Means** - Specify number of clusters
- **Spectral** - Graph-based clustering

### 3. Parameter Configuration

Each method displays configurable parameters below its dropdown:

| Method | Key Parameters |
|--------|---------------|
| UMAP | n_neighbors, min_dist, metric |
| t-SNE | perplexity, metric, max_iter |
| PCA | whiten, svd_solver |
| HDBSCAN | min_cluster_size, min_samples |
| K-Means | n_clusters |

### 4. Comparison Mode

Toggle "Compare two dimension reduction methods" to see side-by-side visualizations.

## Running Analysis

1. Select an embedding model
2. Choose dimension reduction method
3. Adjust parameters if needed
4. Choose clustering method
5. Click **Run Analysis**

The visualization will update with:

- Scatter plot colored by domain
- Cluster assignments in hover tooltips
- Silhouette score and cluster count in title

## Exporting Data

### Selected Points

Use lasso or box selection on the plot, then:

- **Export to JSON**: Saves structured data
- **Export to CSV**: Tabular format
- **Copy to Clipboard**: For pasting

### Parameters

Click **Export Parameters (YAML)** to save current configuration:

```yaml
# Example: 20260118-0930-params.yaml
exported_at: '2026-01-18T09:30:00'
model: SAPBERT
dimension_reduction:
  method: umap
  parameters:
    n_neighbors: 15
    min_dist: 0.1
    metric: cosine
clustering:
  method: hdbscan
  parameters:
    min_cluster_size: 15
    min_samples: 5
```

## Command Line Options

```bash
python domains_clustering_interactive_plots_dash.py [OPTIONS]

Options:
  --config-path PATH    Path to config INI file
  --param-path PATH     Path to parameters INI file
  --port INT            Server port (default: 8050)
  --no-progress         Disable progress bars
```

## Next Steps

- [Configuration](configuration.md): Customize data paths
- [Method Selection](../user-guide/method-selection.md): Learn about each method
- [Parameter Tuning](../user-guide/parameters.md): Optimize your analysis
