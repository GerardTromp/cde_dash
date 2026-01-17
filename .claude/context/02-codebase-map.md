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
├── utils/                            # Utility modules
│   ├── argparse.py                   # CLI argument parsing
│   ├── dash_app.py                   # Dash app creation & callbacks
│   ├── dash_app_functions.py         # UI helper functions
│   ├── functions.py                  # Core data loading & config
│   ├── internal_functions.py         # Text processing & plotting helpers
│   └── run_analysis.py               # ML analysis pipeline
├── domains_clustering_interactive_plots_dash.py  # Main entry point
├── __init__.py                       # Package init
├── requirements_interactive_shr.txt  # Python dependencies
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
- `--umapkwargs`: UMAP key=value overrides
- `--tsnekwargs`: t-SNE key=value overrides

## Module Dependencies

```
domains_clustering_interactive_plots_dash.py
    ├── utils/functions.py
    │   └── (pandas, numpy, plotly, umap, sklearn, configparser)
    ├── utils/dash_app.py
    │   └── utils/dash_app_functions.py
    │   └── utils/functions.py (logger)
    ├── utils/argparse.py
    │   └── (argparse)
    ├── utils/internal_functions.py
    │   └── (re, numpy, pandas, plotly)
    └── utils/run_analysis.py
        └── utils/functions.py (logger)
        └── (umap, sklearn, numpy)
```

## Hot Files (Frequently Modified)

Based on git history:

| File | Change Frequency | Last Modified |
|------|------------------|---------------|
| `utils/dash_app.py` | High | Parameter updating work |
| `utils/dash_app_functions.py` | High | UI parameter inputs |
| `utils/functions.py` | Medium | Config loading, embedding |
| `utils/run_analysis.py` | Medium | Dim reduction params |
| `domains_clustering_interactive_plots_dash.py` | Medium | Main orchestration |

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

### utils/functions.py
- `load_domain_mapping()` - Load domain CSV/JSON
- `load_cde_data()` - Load and filter CDE data
- `load_embedding_models()` - Load precomputed embeddings
- `load_configs()` - Parse INI configuration
- `config_to_dict()` - Convert configparser to dict
- `setup_logging()` - Configure logging

### utils/dash_app.py
- `create_dash_app()` - Build Dash layout
- `setup_callbacks()` - Register all callbacks

### utils/run_analysis.py
- `run_analysis()` - Full analysis pipeline
- `apply_dimensionality_reduction()` - t-SNE/UMAP
- `apply_clustering()` - HDBSCAN
- `evaluate_clustering()` - Metrics calculation

### utils/internal_functions.py
- `_truncate_text()` - Text truncation for tooltips
- `_get_color_and_shape()` - Marker styling
- `_create_faceted_comparison_figure()` - Main plot generation
- `_clean_text()` - Text sanitization
