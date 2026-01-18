# Installation

## Prerequisites

- Python 3.10 or higher
- pip or conda package manager
- Git (optional, for development)

## Install from Source

### 1. Clone the Repository

```bash
git clone https://github.com/GerardTromp/cde_dash.git
cd cde_dash
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Or using conda
conda create -n cde_clustering python=3.12
conda activate cde_clustering
```

### 3. Install Dependencies

```bash
pip install -r requirements_interactive_shr.txt
```

### Required Packages

| Package | Purpose |
|---------|---------|
| dash | Web framework |
| dash-bootstrap-components | UI styling |
| plotly | Visualization |
| pandas | Data processing |
| numpy | Numerical operations |
| scikit-learn | ML algorithms |
| umap-learn | UMAP dimension reduction |
| pyyaml | Parameter export |
| pyperclip | Clipboard support |

## Configuration

### Data Files

The application expects:

1. **Domain mapping file**: CSV or JSON mapping domains to CDEs
2. **CDE data file**: CSV with CDE metadata
3. **Embedding files**: Precomputed embeddings as CSV/text files

Default paths are configured in `config/cde_analysis.ini`. See [Configuration](configuration.md) for details.

### Parameters

Algorithm parameters can be configured in `config/parameters.ini` or modified at runtime via the web UI.

## Verify Installation

```bash
# Test imports
python -c "from utils.methods import MethodRegistry; print(MethodRegistry.list_dim_reduction())"

# Expected output:
# {'umap': 'UMAP', 'tsne': 't-SNE', 'pca': 'PCA'}
```

## Next Steps

- [Quick Start](quickstart.md): Run your first analysis
- [Configuration](configuration.md): Customize paths and parameters
