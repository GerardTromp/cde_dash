# Architecture Overview

This document describes the technical architecture of the CDE Clustering Application.

## Architectural Style

The application follows a **Modular Plugin Architecture** with MVC-like separation:

- **View Layer**: Dash/Plotly web interface
- **Controller**: Dash callbacks for event handling
- **Model/Logic**: Analysis functions and method plugins
- **Plugin System**: Registry-based method modules

## Component Diagram

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

## Major Components

### 1. InteractiveClusteringAnalyzer

**Location**: `domains_clustering_interactive_plots_dash.py:52`

Central orchestrator that:

- Manages embedding models and data
- Coordinates analysis workflows
- Owns the Dash application instance
- Uses method delegation pattern

### 2. Method Registry System

**Location**: `utils/methods/`

Plugin system enabling modular method registration:

```
utils/methods/
├── __init__.py           # Re-exports MethodRegistry
├── base.py               # Protocol definitions
├── registry.py           # Central registry
├── dim_reduction/        # Dimension reduction plugins
└── clustering/           # Clustering plugins
```

### 3. Data Loading Layer

**Location**: `utils/functions.py`

Handles all external data operations:

- Configuration parsing
- Domain mapping
- CDE data loading
- Embedding loading

### 4. Analysis Pipeline

**Location**: `utils/run_analysis.py`

Orchestrates the analysis workflow:

- `run_analysis_single()`: Registry-based analysis
- `create_single_plot()`: Visualization generation
- `create_comparison_plot()`: Side-by-side views

### 5. Visualization Layer

**Location**: `utils/dash_app.py`

Web interface components:

- Layout definition
- Callback registration
- User interaction handling

## Data Flow

```
1. Startup
   Config → Domain Mapping → CDE Data → Embeddings → Methods Registered

2. User Interaction
   Select Method → Parameters Populated → Configure → Run Analysis

3. Analysis
   Embeddings → Dim Reduction → Clustering → Metrics → Visualization

4. Export
   Selection → Extraction → JSON/CSV/YAML
```

## Key Design Patterns

### Registry Pattern

Methods self-register via decorators:

```python
@MethodRegistry.register_dim_reduction
class UMAPMethod:
    method_id = "umap"
    ...
```

### Protocol Contracts

Type-safe interfaces using `typing.Protocol`:

```python
@runtime_checkable
class DimReductionMethod(Protocol):
    name: str
    method_id: str

    def fit_transform(...): ...
```

### Schema-Driven UI

Parameters defined declaratively:

```python
@staticmethod
def param_schema():
    return {
        "n_neighbors": {
            "type": "int",
            "min": 2,
            "max": 200
        }
    }
```

### Method Delegation

Analyzer imports functions as class attributes:

```python
class InteractiveClusteringAnalyzer:
    run_analysis_single = run_analysis_single
    create_single_plot = create_single_plot
```

## Technology Stack

| Layer | Technology |
|-------|------------|
| Web Framework | Dash |
| UI Components | Dash Bootstrap Components |
| Visualization | Plotly |
| ML/Clustering | scikit-learn |
| Dim Reduction | UMAP-learn, scikit-learn |
| Data Processing | Pandas, NumPy |
| Configuration | configparser, PyYAML |

## See Also

- [Method Registry](registry.md): Registry implementation details
- [Plugin System](plugins.md): Adding new methods
