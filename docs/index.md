# CDE Clustering Application

Interactive clustering analysis for Common Data Elements (CDEs) using embedding-based visualization.

## Overview

This application provides an interactive web interface for exploring and clustering medical Common Data Elements using state-of-the-art embedding models and dimensionality reduction techniques.

### Key Features

- **Multiple Embedding Models**: Support for SAPBERT, MedCPT, and other biomedical embeddings
- **Modular Dimension Reduction**: UMAP, t-SNE, and PCA with configurable parameters
- **Flexible Clustering**: HDBSCAN, DBSCAN, K-Means, and Spectral clustering
- **Interactive Visualization**: Plotly-based plots with lasso/box selection
- **Comparison Mode**: Side-by-side comparison of dimension reduction methods
- **Data Export**: Export selected points to JSON, CSV, or clipboard
- **Parameter Export**: Save analysis parameters to YAML for reproducibility

## Quick Start

```bash
# Activate environment
source venv/bin/activate

# Run the application
python domains_clustering_interactive_plots_dash.py --port 8050
```

Then open [http://127.0.0.1:8050](http://127.0.0.1:8050) in your browser.

## Documentation Sections

- **[Getting Started](getting-started/installation.md)**: Installation and initial setup
- **[User Guide](user-guide/overview.md)**: How to use the application
- **[Architecture](architecture/overview.md)**: Technical documentation
- **[Developer Guide](developer/adding-methods.md)**: Extending the application

## Architecture Highlights

The application uses a **modular registry-based architecture** that makes it easy to add new dimension reduction or clustering methods:

```python
from utils.methods import MethodRegistry

@MethodRegistry.register_dim_reduction
class MyCustomMethod:
    name = "My Method"
    method_id = "my_method"

    @staticmethod
    def default_params():
        return {"param1": 10}

    @staticmethod
    def param_schema():
        return {"param1": {"type": "int", "default": 10, "min": 1, "max": 100}}

    def fit_transform(self, embeddings, params):
        # Your implementation
        pass
```

## Technology Stack

| Component | Technology |
|-----------|------------|
| Web Framework | Dash |
| Visualization | Plotly |
| UI Components | Dash Bootstrap Components |
| ML Pipeline | scikit-learn, UMAP-learn |
| Data Processing | Pandas, NumPy |

## License

This project is developed at Stellenbosch University for medical informatics research.
