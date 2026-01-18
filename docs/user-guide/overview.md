# User Guide Overview

This guide covers the main features of the CDE Clustering Application.

## Application Workflow

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ 1. Select Model  │ --> │ 2. Choose Methods│ --> │ 3. Run Analysis  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
                                                           │
                                                           v
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ 6. Export Data   │ <-- │ 5. Select Points │ <-- │ 4. View Results  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

## Key Concepts

### Embedding Models

CDEs are represented as high-dimensional vectors (embeddings) that capture semantic meaning. Different models may capture different aspects:

- **SAPBERT**: Trained on UMLS, good for biomedical concepts
- **MedCPT**: Trained for medical passage retrieval

### Dimension Reduction

High-dimensional embeddings (768+ dimensions) are reduced to 2D for visualization:

| Method | Best For | Speed |
|--------|----------|-------|
| UMAP | Global structure | Fast |
| t-SNE | Local neighborhoods | Medium |
| PCA | Quick overview | Very fast |

### Clustering

Points are grouped based on their positions in the reduced space:

| Method | Finds # Clusters | Handles Noise |
|--------|-----------------|---------------|
| HDBSCAN | Automatic | Yes |
| DBSCAN | Automatic | Yes |
| K-Means | You specify | No |
| Spectral | You specify | No |

## Interface Sections

### Header
- Application title

### Embedding Model Selection
- Radio buttons to choose the embedding model
- Status indicator shows if model is loaded

### Method Selection
- **Left card**: Dimension reduction dropdown + parameters
- **Right card**: Clustering dropdown + parameters
- Toggle for comparison mode

### Action Row
- **Run Analysis**: Execute with current settings
- **Export Parameters (YAML)**: Save configuration

### Visualization
- Interactive scatter plot
- Points colored by domain
- Hover for CDE details
- Lasso/box selection tools

### Data Export
- Selection counter
- Export to JSON/CSV/Clipboard

## Keyboard Shortcuts

The plot supports standard Plotly interactions:

| Action | Shortcut |
|--------|----------|
| Zoom | Scroll wheel |
| Pan | Click + drag |
| Lasso select | Click lasso tool, then draw |
| Box select | Click box tool, then draw |
| Reset zoom | Double-click |
| Download plot | Camera icon |

## Guides

- [Method Selection](method-selection.md): Choosing the right methods
- [Parameter Tuning](parameters.md): Optimizing analysis
- [Data Export](export.md): Saving your results
- [Comparison Mode](comparison.md): Side-by-side analysis
