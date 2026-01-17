# Architectural Decisions

## ADR-001: Precomputed Embeddings over Runtime Computation

### Status
Accepted

### Context
Originally the code was designed to compute embeddings at runtime using sentence-transformers. This required loading large transformer models (SAPBERT, MedCPT) and processing text on each run.

### Decision
Switch to precomputed embeddings stored as CSV/text files. Embeddings are loaded and subset using a selection vector JSON file.

### Rationale
- Faster startup time (no model loading)
- Reduced memory requirements
- Reproducible results
- Allows running on machines without GPU

### Consequences
- Requires preprocessing step to generate embeddings
- Need to maintain selection vector file in sync with data
- Adding new CDEs requires regenerating embeddings

---

## ADR-002: Method Delegation over Inheritance

### Status
Accepted

### Context
The `InteractiveClusteringAnalyzer` class needs access to many utility functions. Options: inheritance, composition, or method delegation.

### Decision
Use method delegation by importing functions and assigning them as class attributes:
```python
load_domain_mapping = load_domain_mapping
run_analysis = run_analysis
```

### Rationale
- Keeps class file compact
- Functions remain testable in isolation
- Clear separation of concerns
- Avoids diamond inheritance problems

### Consequences
- Slightly unusual pattern may confuse new developers
- IDE may not provide full autocomplete for delegated methods

---

## ADR-003: Dash over Flask/Streamlit

### Status
Accepted

### Context
Needed an interactive web interface for CDE clustering visualization with point selection and data export.

### Decision
Use Dash with Plotly and Bootstrap components.

### Rationale
- Native Plotly integration for interactive plots
- Lasso/box selection built into Plotly
- Callbacks provide reactive updates
- Bootstrap components for professional UI

### Consequences
- Dash callback complexity for stateful interactions
- Some limitations on custom JavaScript

---

## ADR-004: Dual Visualization (t-SNE + UMAP)

### Status
Accepted

### Context
Different dimensionality reduction methods preserve different aspects of the embedding space.

### Decision
Always show t-SNE and UMAP side-by-side in a faceted comparison figure.

### Rationale
- t-SNE better for local structure, UMAP for global
- Visual comparison helps validate clustering
- Users can assess which method suits their analysis

### Consequences
- Double computation time
- More complex figure generation
- Larger plot area required

---

## ADR-005: INI Configuration Files

### Status
Accepted

### Context
Need flexible configuration for data paths, model selection, and algorithm parameters.

### Decision
Use Python's configparser with INI format files.

### Rationale
- Human-readable format
- Built-in Python support
- Sections for logical grouping
- Easy to edit without code changes

### Consequences
- Custom parsing for complex types (lists, tuples, None)
- Less expressive than YAML/JSON for nested structures
- Type inference required in `config_to_dict()`

---

## ADR-006: HDBSCAN for Clustering

### Status
Accepted

### Context
Need clustering algorithm that works well with embedding spaces of varying density.

### Decision
Use HDBSCAN with configurable min_cluster_size and min_samples.

### Rationale
- Handles noise points explicitly (label -1)
- Doesn't require specifying number of clusters
- Works well with high-dimensional data
- Consistent with medical/scientific NLP practices

### Consequences
- May produce many noise points with default parameters
- Sensitive to min_cluster_size setting
- Requires sklearn 1.0+ for built-in implementation

---

## ADR-007: Centralized Parameter Management

### Status
In Progress (current development focus)

### Context
Parameters for UMAP, t-SNE, and HDBSCAN are scattered and hard to modify at runtime.

### Decision
Move parameters to central dictionaries on the analyzer instance, loadable from INI files and modifiable via Dash UI.

### Rationale
- Single source of truth for parameters
- Runtime modification via web interface
- Easy to save/load parameter configurations

### Consequences
- Requires UI components for parameter editing
- Need callbacks to sync UI state with dictionaries
- Current work-in-progress (see git history)

---

## Decision Log (from Git History)

| Date | Commit | Decision |
|------|--------|----------|
| Recent | `8aa7607` | Code functional - baseline working state |
| Recent | `bac5458` | Moved parameters to central dict |
| Recent | `66025d8` | Created param-update branch |
| Recent | `3f97f3b` | Added dash parameter tab, moved dash functions |
| Recent | `243f94a` | Parameter updating - new branch for re-clustering |
