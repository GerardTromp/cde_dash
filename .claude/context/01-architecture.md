# Architecture Overview

## Architectural Style
**Monolithic Application with MVC-like Separation**

The application follows a single-process architecture with clear separation of concerns:
- **View Layer**: Dash/Plotly web interface (`dash_app.py`, `dash_app_functions.py`)
- **Controller**: Callbacks and event handlers in `setup_callbacks()`
- **Model/Logic**: Analysis functions (`run_analysis.py`, `functions.py`)

## Major Components

### 1. InteractiveClusteringAnalyzer (Main Class)
Location: `domains_clustering_interactive_plots_dash.py:49`

Central orchestrator that:
- Manages embedding models and data
- Coordinates analysis workflows
- Owns the Dash application instance
- Uses method delegation pattern (imports methods from utility modules)

### 2. Data Loading Layer
Location: `utils/functions.py`

- `load_domain_mapping()`: Loads domain-to-CDE mappings (CSV/JSON)
- `load_cde_data()`: Loads CDE dataset and filters by domain
- `load_embedding_models()`: Loads precomputed embeddings
- `load_configs()`: INI config file parsing

### 3. Analysis Pipeline
Location: `utils/run_analysis.py`

- `apply_dimensionality_reduction()`: t-SNE/UMAP reduction
- `apply_clustering()`: HDBSCAN clustering
- `evaluate_clustering()`: Silhouette score, coverage metrics
- `run_analysis()`: Orchestrates full analysis pipeline

### 4. Visualization Layer
Location: `utils/dash_app.py`, `utils/internal_functions.py`

- `create_dash_app()`: Builds Dash layout with Bootstrap
- `setup_callbacks()`: Registers interactive callbacks
- `_create_faceted_comparison_figure()`: Creates side-by-side t-SNE/UMAP plots

## Technology Stack

| Layer | Technology |
|-------|------------|
| Web Framework | Dash 2.6+ |
| UI Components | Dash Bootstrap Components |
| Visualization | Plotly 5.0+ |
| ML/Clustering | scikit-learn (HDBSCAN, t-SNE) |
| Dim Reduction | UMAP-learn, scikit-learn TSNE |
| Embeddings | Sentence Transformers, Transformers |
| Data Processing | Pandas, NumPy |
| Configuration | configparser (INI files) |

## Component Communication

```
┌─────────────────────────────────────────────────────────────┐
│                    Dash Web Interface                        │
│  (Model Selector, Clustering Plot, Export Controls)         │
└──────────────────────────┬──────────────────────────────────┘
                           │ Callbacks
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              InteractiveClusteringAnalyzer                   │
│  - embedding_models: Dict                                    │
│  - analysis_results: Dict                                    │
│  - config: Dict                                              │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├────────────────┬────────────────┬──────────────────┐
       ▼                ▼                ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ functions.py │ │run_analysis  │ │internal_func │ │dash_app_func │
│ Data Loading │ │ML Pipeline   │ │Text/Plotting │ │UI Helpers    │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

## Data Flow

1. **Startup**: Config files loaded → Domain mapping loaded → CDE data filtered → Embeddings loaded
2. **Analysis Trigger**: User selects model → `run_analysis()` called
3. **Pipeline**: Embeddings → StandardScaler → t-SNE/UMAP → HDBSCAN → Metrics
4. **Visualization**: Results → `create_faceted_plots()` → Plotly Figure → Dash Graph
5. **Export**: User selects points → Callback extracts data → JSON/CSV/Clipboard

## Key Design Decisions

- **Precomputed Embeddings**: Embeddings loaded from files rather than computed at runtime
- **Method Delegation**: Analyzer class imports methods from modules rather than inheriting
- **Dual Visualization**: Always shows t-SNE and UMAP side-by-side for comparison
- **INI Configuration**: Uses configparser for flexible config management
