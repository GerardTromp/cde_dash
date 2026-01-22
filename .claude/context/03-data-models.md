# Data Models

## No Database

This application does not use a database. All data is file-based:
- CSV/JSON files for domain mappings and CDE data
- NumPy text files for precomputed embeddings
- INI files for configuration

## Key Data Structures

### 1. InteractiveClusteringAnalyzer State

```python
class InteractiveClusteringAnalyzer:
    # Visual styling
    d3_colors: List[str]           # 20 D3 category colors
    marker_shapes: List[str]        # 8 Plotly marker shapes

    # Data storage
    embedding_models: Dict[str, np.ndarray]  # model_name -> embedding matrix
    tokenizers: Dict                # (unused)
    domain_mapping: pd.DataFrame    # tinyid -> domain mapping
    cde_data: pd.DataFrame          # Raw CDE data
    filtered_cdes: pd.DataFrame     # Processed CDE data with domains

    # Analysis results
    all_metrics: Dict[str, Dict]    # model -> method -> metrics
    analysis_results: Dict[str, Dict]  # model -> full results

    # Configuration
    config: Dict                    # CDEAnalysis config section
    hdbscan_params: Dict            # HDBSCAN parameters
    umap_params: Dict               # UMAP parameters
    tsne_params: Dict               # t-SNE parameters
    analysis_params: Dict           # (unused)

    # Dash application
    app: dash.Dash                  # Dash app instance
```

### 2. Domain Mapping DataFrame

Loaded from CSV, maps CDE tinyIds to domains.

| Column | Type | Description |
|--------|------|-------------|
| `tinyid` | str | Unique CDE identifier |
| `domain` | str | Domain category label |

### 3. CDE DataFrame (Raw)

Loaded from CSV, contains CDE metadata.

| Column | Type | Description |
|--------|------|-------------|
| `tinyId` | str | Unique identifier |
| `Name` / `name` | str | CDE name |
| `Question` / `question` | str | Associated question |
| `Definition` / `definition` | str | CDE definition |
| `permissibleValues` | str | Allowed values |
| `designations` | list | Alternative names (optional) |
| `definitions` | list | Multiple definitions (optional) |

### 4. Processed CDE DataFrame (filtered_cdes)

After `extract_text_fields()` processing:

| Column | Type | Description |
|--------|------|-------------|
| `tinyId` | str | Original identifier |
| `name` | str | Cleaned name |
| `question` | str | Cleaned question |
| `definition` | str | Cleaned definition |
| `permissible_values` | str | Cleaned values |
| `combined_text` | str | All text concatenated |
| `domain` | str | Mapped domain label |
| (original columns) | various | Preserved from raw data |

### 5. Analysis Results Dict

Returned by `run_analysis()`:

```python
{
    "model_name": str,              # e.g., "sapbert"
    "filtered_cdes": pd.DataFrame,  # Reference to processed data
    "original_embeddings": np.ndarray,  # Shape: (n_samples, embedding_dim)
    "visualization_embeddings": {
        "tsne": np.ndarray,         # Shape: (n_samples, 2)
        "umap": np.ndarray          # Shape: (n_samples, 2)
    },
    "clustering_results": {
        "tsne": {
            "cluster_labels": np.ndarray,  # Shape: (n_samples,)
            "clusterer": HDBSCAN
        },
        "umap": {
            "cluster_labels": np.ndarray,
            "clusterer": HDBSCAN
        }
    }
}
```

### 6. Metrics Dict

From `evaluate_clustering()`:

```python
{
    "silhouette_score": float,      # -1 to 1, higher is better
    "coverage": float,              # Fraction of points in clusters
    "n_clusters": int,              # Number of clusters found
    "n_noise": int,                 # Points marked as noise (-1)
    "avg_cluster_size": float       # Mean cluster size
}
```

### 7. Configuration Dict

Parsed from INI files:

```python
# config/cde_analysis.ini -> config["CDEAnalysis"]
{
    "domains": str,                 # Path to domain mapping file
    "alltext": str,                 # Path to CDE data file
    "models": List[str] | str,      # Model names to load
    "embedtext": List[str] | str,   # Embedding text types
    "template": str,                # File path template
    "selectvec": str                # Index selection JSON path
}

# config/parameters.ini
{
    "UMAP": {
        "n_neighbors": int,
        "min_dist": float,
        "metric": str,
        ...
    },
    "TSNE": {
        "perplexity": int,
        "learning_rate": float,
        ...
    },
    "HDBSCAN": {
        "min_cluster_size": int,
        "min_samples": int,
        ...
    }
}
```

## Data Validation Patterns

### Text Cleaning (`_clean_text`)
- Remove excess whitespace
- Strip HTML tags
- Remove special characters (keep alphanumeric, basic punctuation)

### Field Extraction (`extract_text_fields`)
- Tries multiple column name variants (Name/name/designation/CDE_Name)
- Falls back to nested structures (designations list)
- Filters out entries with combined_text < 5 characters

### Domain Mapping
- Deduplicates on tinyid (keeps first occurrence)
- Logs duplicate removal count
- Labels unmapped CDEs as "Unknown"
