# Architecture Overview

## Architectural Style
**Modular Plugin Architecture with MVC-like Separation**

The application follows a plugin-based architecture with clear separation of concerns:
- **View Layer**: Dash/Plotly web interface (`dash_app.py`, `dash_app_functions.py`)
- **Controller**: Callbacks and event handlers in `setup_callbacks()`
- **Model/Logic**: Analysis functions (`run_analysis.py`, `functions.py`)
- **Plugin System**: Registry-based method modules (`utils/methods/`)

## Major Components

### 1. InteractiveClusteringAnalyzer (Main Class)
Location: `domains_clustering_interactive_plots_dash.py:52`

Central orchestrator that:
- Manages embedding models and data
- Coordinates analysis workflows
- Owns the Dash application instance
- Uses method delegation pattern (imports methods from utility modules)

### 2. Method Registry System (NEW)
Location: `utils/methods/`

A modular plugin system for dimension reduction and clustering methods:

```
utils/methods/
├── __init__.py           # Re-exports MethodRegistry
├── base.py               # Protocol definitions (contracts)
├── registry.py           # Central MethodRegistry class
├── dim_reduction/        # Dimension reduction plugins
│   ├── umap_method.py    # UMAP
│   ├── tsne.py           # t-SNE
│   └── pca.py            # PCA
└── clustering/           # Clustering plugins
    ├── hdbscan.py        # HDBSCAN
    ├── dbscan.py         # DBSCAN
    ├── kmeans.py         # K-Means
    └── spectral.py       # Spectral Clustering
```

**Key Features:**
- Decorator-based registration (`@MethodRegistry.register_dim_reduction`)
- Protocol-based contracts (typing.Protocol) for type safety
- Schema-driven parameter UI generation
- Runtime method discovery

### 3. Data Loading Layer
Location: `utils/functions.py`

- `load_domain_mapping()`: Loads domain-to-CDE mappings (CSV/JSON)
- `load_cde_data()`: Loads CDE dataset and filters by domain
- `load_embedding_models()`: Loads precomputed embeddings
- `load_configs()`: INI config file parsing

### 4. Analysis Pipeline
Location: `utils/run_analysis.py`

- `run_analysis_single()`: Registry-based analysis using selected methods
- `apply_dimensionality_reduction()`: Legacy t-SNE/UMAP reduction
- `apply_clustering()`: Legacy HDBSCAN clustering
- `evaluate_clustering()`: Silhouette score, coverage metrics
- `create_single_plot()`: Single method visualization
- `create_comparison_plot()`: Side-by-side method comparison

### 5. Visualization Layer
Location: `utils/dash_app.py`, `utils/internal_functions.py`

- `create_dash_app()`: Builds Dash layout with method selectors
- `setup_callbacks()`: Registers interactive callbacks
- `param_inputs_from_schema()`: Dynamic parameter UI generation

### 6. Parameter Export
Location: `utils/export_params.py`

- `export_params_yaml()`: Exports current parameters to timestamped YAML

## Technology Stack

| Layer | Technology |
|-------|------------|
| Web Framework | Dash 2.6+ |
| UI Components | Dash Bootstrap Components |
| Visualization | Plotly 5.0+ |
| ML/Clustering | scikit-learn (HDBSCAN, DBSCAN, K-Means, Spectral) |
| Dim Reduction | UMAP-learn, scikit-learn (TSNE, PCA) |
| Embeddings | Sentence Transformers, Transformers |
| Data Processing | Pandas, NumPy |
| Configuration | configparser (INI), PyYAML |

## Component Communication

```
┌─────────────────────────────────────────────────────────────┐
│                    Dash Web Interface                        │
│  (Method Selectors, Parameter Inputs, Plot, Export)         │
└──────────────────────────┬──────────────────────────────────┘
                           │ Callbacks
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              InteractiveClusteringAnalyzer                   │
│  - embedding_models: Dict                                    │
│  - analysis_results: Dict                                    │
│  - {method}_params: Dict (dynamic per-method)               │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├────────────────┬────────────────┬──────────────────┐
       ▼                ▼                ▼                  ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ functions.py │ │run_analysis  │ │MethodRegistry│ │export_params │
│ Data Loading │ │ML Pipeline   │ │Method Lookup │ │YAML Export   │
└──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
                        │
                        ▼
        ┌───────────────────────────────────────┐
        │     utils/methods/ Plugin System       │
        │  ┌─────────────┐  ┌─────────────┐     │
        │  │dim_reduction│  │  clustering │     │
        │  │ UMAP, t-SNE │  │HDBSCAN, etc │     │
        │  │ PCA         │  │             │     │
        │  └─────────────┘  └─────────────┘     │
        └───────────────────────────────────────┘
```

## Data Flow

1. **Startup**: Config files loaded → Domain mapping loaded → CDE data filtered → Embeddings loaded → Methods registered
2. **Method Selection**: User selects dim reduction + clustering → Parameters dynamically populated
3. **Analysis Trigger**: User clicks "Run Analysis" → `run_analysis_single()` called
4. **Pipeline**: Embeddings → Method.fit_transform()/fit_predict() → Metrics
5. **Visualization**: Results → `create_single_plot()` or `create_comparison_plot()` → Plotly Figure
6. **Export**:
   - Data: User selects points → Callback extracts data → JSON/CSV/Clipboard
   - Params: User clicks export → `export_params_yaml()` → YAML file

## Key Design Decisions

- **Precomputed Embeddings**: Embeddings loaded from files rather than computed at runtime
- **Method Delegation**: Analyzer class imports methods from modules rather than inheriting
- **Registry Pattern**: Methods self-register via decorators for extensibility
- **Protocol Contracts**: Type-safe method interfaces using typing.Protocol
- **Schema-Driven UI**: Parameter inputs generated from method schemas
- **Single Selection**: Only one dim reduction and one clustering method active at a time
- **Comparison Mode**: Optional toggle to compare two dim reduction methods side-by-side
- **YAML Parameter Export**: Timestamped export for reproducibility
