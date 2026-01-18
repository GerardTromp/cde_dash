# Codebase Map

## Directory Structure

```
clust_app/
├── .claude/                          # Claude checkpoint system
│   ├── checkpoints/                  # Session checkpoints (gitignored)
│   ├── context/                      # Context documentation
│   ├── memory-bank/                  # Persistent memory
│   ├── sessions/                     # Session data (gitignored)
│   ├── CHECKPOINT_PROMPTS.md         # Checkpoint usage prompts
│   ├── CHECKPOINT_SYSTEM.md          # System documentation
│   └── QUICK_START.md                # Quick start guide
├── config/                           # Configuration files (external)
│   ├── cde_analysis.ini              # Data paths, model config
│   └── parameters.ini                # UMAP/TSNE/HDBSCAN parameters
├── data/                             # Data files (external)
│   ├── domains/                      # Domain mapping files
│   └── embeddings/                   # Precomputed embedding matrices
├── docs/                             # Documentation (mkdocs)
│   ├── index.md                      # Home page
│   ├── getting-started/              # Setup guides
│   ├── user-guide/                   # Usage documentation
│   ├── architecture/                 # Technical docs
│   └── api/                          # API reference
├── utils/                            # Utility modules
│   ├── methods/                      # Method plugin system (NEW)
│   │   ├── __init__.py               # Re-exports MethodRegistry
│   │   ├── base.py                   # Protocol definitions
│   │   ├── registry.py               # Central registry
│   │   ├── dim_reduction/            # Dim reduction plugins
│   │   │   ├── __init__.py
│   │   │   ├── umap_method.py        # UMAP
│   │   │   ├── tsne.py               # t-SNE
│   │   │   └── pca.py                # PCA
│   │   └── clustering/               # Clustering plugins
│   │       ├── __init__.py
│   │       ├── hdbscan.py            # HDBSCAN
│   │       ├── dbscan.py             # DBSCAN
│   │       ├── kmeans.py             # K-Means
│   │       └── spectral.py           # Spectral
│   ├── argparse.py                   # CLI argument parsing
│   ├── dash_app.py                   # Dash app creation & callbacks
│   ├── dash_app_functions.py         # UI helper functions
│   ├── export_params.py              # YAML parameter export (NEW)
│   ├── functions.py                  # Core data loading & config
│   ├── internal_functions.py         # Text processing & plotting helpers
│   └── run_analysis.py               # ML analysis pipeline
├── domains_clustering_interactive_plots_dash.py  # Main entry point
├── __init__.py                       # Package init
├── requirements_interactive_shr.txt  # Python dependencies
├── mkdocs.yml                        # MkDocs configuration
└── .gitignore                        # Git ignore rules
```

## Entry Points

| Entry Point | Description | Usage |
|-------------|-------------|-------|
| `domains_clustering_interactive_plots_dash.py` | Main application | `python domains_clustering_interactive_plots_dash.py --port 8050` |

### CLI Arguments
- `--config-path`: Path to INI config file (default: `config/cde_analysis.ini`)
- `--param-path`: Path to parameters INI file (default: `config/parameters.ini`)
- `--port`: Dash server port (default: 8050)
- `--no-progress`: Disable progress bars

## Module Dependencies

```
domains_clustering_interactive_plots_dash.py
    ├── utils/functions.py
    │   └── (pandas, numpy, plotly, umap, sklearn, configparser)
    ├── utils/dash_app.py
    │   ├── utils/dash_app_functions.py
    │   ├── utils/methods (MethodRegistry)
    │   ├── utils/export_params.py
    │   └── utils/functions.py (logger)
    ├── utils/argparse.py
    │   └── (argparse)
    ├── utils/internal_functions.py
    │   └── (re, numpy, pandas, plotly)
    └── utils/run_analysis.py
        ├── utils/functions.py (logger)
        ├── utils/methods (MethodRegistry)
        └── (umap, sklearn, numpy)

utils/methods/
    ├── __init__.py
    │   └── registry.py (MethodRegistry)
    ├── registry.py
    │   └── (typing)
    ├── base.py
    │   └── (typing, numpy)
    ├── dim_reduction/
    │   ├── umap_method.py → @MethodRegistry.register_dim_reduction
    │   ├── tsne.py        → @MethodRegistry.register_dim_reduction
    │   └── pca.py         → @MethodRegistry.register_dim_reduction
    └── clustering/
        ├── hdbscan.py     → @MethodRegistry.register_clustering
        ├── dbscan.py      → @MethodRegistry.register_clustering
        ├── kmeans.py      → @MethodRegistry.register_clustering
        └── spectral.py    → @MethodRegistry.register_clustering
```

## Hot Files (Frequently Modified)

Based on git history:

| File | Change Frequency | Last Modified |
|------|------------------|---------------|
| `utils/dash_app.py` | High | Modular architecture refactor |
| `utils/run_analysis.py` | High | Added run_analysis_single() |
| `utils/dash_app_functions.py` | High | Added param_inputs_from_schema() |
| `utils/methods/*.py` | New | Modular architecture refactor |
| `domains_clustering_interactive_plots_dash.py` | Medium | Method bindings |

## Stable Files

| File | Status | Notes |
|------|--------|-------|
| `utils/argparse.py` | Stable | CLI interface defined |
| `utils/internal_functions.py` | Stable | Text helpers, plotting |
| `__init__.py` | Stable | Empty package init |

## Key Functions by File

### domains_clustering_interactive_plots_dash.py
- `InteractiveClusteringAnalyzer` class (main orchestrator)
- `main()` - entry point, loads configs and starts Dash

### utils/methods/registry.py
- `MethodRegistry.register_dim_reduction()` - Decorator for dim reduction
- `MethodRegistry.register_clustering()` - Decorator for clustering
- `MethodRegistry.get_dim_reduction()` - Get method by ID
- `MethodRegistry.get_clustering()` - Get method by ID
- `MethodRegistry.list_dim_reduction()` - List available methods
- `MethodRegistry.list_clustering()` - List available methods

### utils/methods/base.py
- `DimReductionMethod` - Protocol for dimension reduction
- `ClusteringMethod` - Protocol for clustering

### utils/functions.py
- `load_domain_mapping()` - Load domain CSV/JSON
- `load_cde_data()` - Load and filter CDE data
- `load_embedding_models()` - Load precomputed embeddings
- `load_configs()` - Parse INI configuration
- `config_to_dict()` - Convert configparser to dict
- `setup_logging()` - Configure logging

### utils/dash_app.py
- `create_dash_app()` - Build Dash layout with method selectors
- `setup_callbacks()` - Register all callbacks (method selection, params, analysis, export)

### utils/dash_app_functions.py
- `param_inputs_from_schema()` - Generate parameter inputs from method schema
- `param_inputs()` - Legacy parameter input builder
- `auto_cast()` - Type conversion for parameter values

### utils/run_analysis.py
- `run_analysis_single()` - Run analysis with registry methods
- `create_single_plot()` - Create single method visualization
- `create_comparison_plot()` - Create side-by-side comparison
- `run_analysis()` - Legacy full analysis pipeline
- `apply_dimensionality_reduction()` - Legacy t-SNE/UMAP
- `apply_clustering()` - Legacy HDBSCAN
- `evaluate_clustering()` - Metrics calculation

### utils/export_params.py
- `export_params_yaml()` - Export parameters to timestamped YAML

### utils/internal_functions.py
- `_truncate_text()` - Text truncation for tooltips
- `_get_color_and_shape()` - Marker styling
- `_create_faceted_comparison_figure()` - Legacy plot generation
- `_clean_text()` - Text sanitization
