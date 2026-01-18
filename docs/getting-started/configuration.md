# Configuration

The application uses INI configuration files for data paths and algorithm parameters.

## Configuration Files

| File | Purpose |
|------|---------|
| `config/cde_analysis.ini` | Data paths, model settings |
| `config/parameters.ini` | Algorithm parameters |

## Data Configuration

### cde_analysis.ini

```ini
[Paths]
domain_mapping = /path/to/domains.csv
cde_data = /path/to/cde_data.csv
embedding_dir = /path/to/embeddings/

[Models]
embedding_models = SAPBERT, MedCPT

[Logging]
log_file = cde_analysis.log
log_level = INFO
```

### Path Settings

| Setting | Description |
|---------|-------------|
| `domain_mapping` | CSV/JSON file mapping domains to CDEs |
| `cde_data` | Main CDE dataset with metadata |
| `embedding_dir` | Directory containing precomputed embeddings |

### Embedding Files

Embedding files should be named to match model names:

```
embeddings/
├── SAPBERT_embeddings.csv
├── MedCPT_embeddings.csv
└── selection_vector.json
```

## Algorithm Parameters

### parameters.ini

```ini
[UMAP]
n_neighbors = 15
min_dist = 0.1
metric = cosine
n_components = 2
random_state = 42

[TSNE]
perplexity = 30
metric = cosine
method = exact
n_components = 2
random_state = 42
max_iter = 1000

[HDBSCAN]
min_cluster_size = 15
min_samples = 5
metric = euclidean
cluster_selection_method = eom
```

!!! note
    Parameters can be overridden at runtime via the web UI.

## Runtime Configuration

### Command Line Override

```bash
python domains_clustering_interactive_plots_dash.py \
    --config-path /custom/config.ini \
    --param-path /custom/params.ini
```

### Environment Variables

Set paths via environment:

```bash
export CDE_CONFIG_PATH=/path/to/config.ini
export CDE_PARAM_PATH=/path/to/params.ini
```

## Parameter Export

After tuning parameters in the UI, export them to YAML:

1. Click **Export Parameters (YAML)**
2. File saved as `YYYYMMDD-HHMM-params.yaml`

Example output:

```yaml
exported_at: '2026-01-18T09:30:00.000000'
model: SAPBERT
dimension_reduction:
  method: umap
  parameters:
    n_neighbors: 20
    min_dist: 0.15
    metric: cosine
clustering:
  method: hdbscan
  parameters:
    min_cluster_size: 10
    min_samples: 3
```

## Separation of Code and Data

!!! important
    The application follows a strict separation of code and data:

    - Configuration files specify paths to external data
    - Data files should NOT be committed to the repository
    - Only demonstration/test data should exist in the codebase
    - User data should never comingle with code

### Recommended Structure

```
project/
├── code/               # Git repository
│   ├── config/         # Configuration templates
│   └── ...
└── data/               # External data (not in git)
    ├── domains/
    ├── embeddings/
    └── exports/
```
