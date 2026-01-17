# Dependencies

## External Dependencies

From `requirements_interactive_shr.txt`:

### Core Data Science
| Package | Version | Purpose |
|---------|---------|---------|
| `numpy` | >=1.21.0 | Array operations, embedding matrices |
| `pandas` | >=1.3.0 | DataFrames for CDE data, domain mapping |
| `scikit-learn` | >=1.0.0 | HDBSCAN, t-SNE, StandardScaler, silhouette_score |

### Visualization
| Package | Version | Purpose |
|---------|---------|---------|
| `matplotlib` | >=3.5.0 | Backend for seaborn (imported but unused directly) |
| `seaborn` | >=0.11.0 | Color palettes (imported but unused directly) |
| `plotly` | >=5.0.0 | Interactive plots, scatter, subplots |

### Web Framework
| Package | Version | Purpose |
|---------|---------|---------|
| `dash` | >=2.6.0 | Web application framework |
| `dash-bootstrap-components` | >=1.2.0 | UI components (Cards, Buttons, Alerts) |

### Machine Learning
| Package | Version | Purpose |
|---------|---------|---------|
| `umap-learn` | >=0.5.0 | UMAP dimensionality reduction |
| `sentence-transformers` | >=2.2.0 | (For embedding generation, not used at runtime) |
| `transformers` | >=4.20.0 | (For embedding generation, not used at runtime) |
| `torch` | >=1.12.0 | (For embedding generation, not used at runtime) |

### Utilities
| Package | Version | Purpose |
|---------|---------|---------|
| `pyperclip` | >=1.8.0 | Clipboard copy functionality |
| `pathlib2` | >=2.3.0 | Path operations (compatibility) |
| `tqdm` | >=4.64.0 | Progress bars during processing |

## Standard Library Usage

| Module | Usage |
|--------|-------|
| `argparse` | CLI argument parsing |
| `configparser` | INI file parsing |
| `json` | JSON file I/O, clipboard data |
| `re` | Text cleaning, regex |
| `ast` | literal_eval for config parsing |
| `os` | File path checking |
| `sys` | (imported but unused) |
| `logging` | Dual console/file logging |
| `datetime` | Timestamps for exports |
| `time` | Performance timing |
| `warnings` | Suppress warnings |
| `collections` | defaultdict (imported but unused) |

## Internal Module Dependencies

```
domains_clustering_interactive_plots_dash.py
├── utils.functions
│   ├── logger (logging.Logger)
│   ├── extract_text_fields
│   ├── create_faceted_plots
│   ├── load_domain_mapping
│   ├── load_cde_data
│   ├── load_embedding_models
│   └── load_configs
├── utils.dash_app
│   ├── create_dash_app
│   └── setup_callbacks
├── utils.argparse
│   └── cde_argparse
├── utils.internal_functions
│   ├── _truncate_text
│   ├── _get_color_and_shape
│   ├── _create_faceted_comparison_figure
│   └── _clean_text
└── utils.run_analysis
    ├── run_analysis
    ├── apply_clustering
    ├── apply_dimensionality_reduction
    └── evaluate_clustering
```

### Cross-Module Dependencies

| Module | Imports From |
|--------|--------------|
| `dash_app.py` | `functions.py` (logger), `dash_app_functions.py` (param_inputs) |
| `run_analysis.py` | `functions.py` (logger, date_time_string) |
| `dash_app_functions.py` | None (standalone) |
| `internal_functions.py` | None (standalone) |
| `argparse.py` | None (standalone) |
| `functions.py` | None (standalone, defines logger) |

## Third-Party Integrations

### File Formats Supported
- **CSV**: pandas read_csv for CDE data, domain mapping
- **JSON**: json.load for selection vectors, pandas read_json for data
- **INI**: configparser for configuration files
- **NumPy text**: np.loadtxt for precomputed embeddings

### External Data Dependencies
The application expects these external files (configured in INI):

| File Type | Purpose | Config Key |
|-----------|---------|------------|
| Domain mapping | tinyid -> domain CSV | `config["CDEAnalysis"]["domains"]` |
| CDE data | Full CDE dataset CSV | `config["CDEAnalysis"]["alltext"]` |
| Embeddings | Precomputed matrices | `config["CDEAnalysis"]["template"]` |
| Selection vector | Index subset JSON | `config["CDEAnalysis"]["selectvec"]` |

## Development Dependencies (Not in requirements)

Likely needed but not listed:
- Python 3.9+ (type hints, walrus operator patterns)
- pip for installation
- Black for formatting (based on `# fmt:` comments)
