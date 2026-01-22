# Gotchas & Known Issues

## Current Known Issues

### 1. Callback Definition Order Issue

**Location**: `utils/dash_app.py:268-294`

**Problem**: The `update_model_status` callback decorator appears after its function is already being used. There's also a mismatched callback structure where `update_params` and `update_model_status` callbacks are interleaved incorrectly.

```python
# Line 268-273: Decorator for update_params callback
@self.app.callback(Output("param-ui", "children"), Input("algo-selector", "value"))
def update_params(algos):
    ...

# Lines 279-294: Another callback decorator, but update_model_status function defined after
@self.app.callback(...)
def update_model_status(selected_model):  # This doesn't match the pattern match decorator
```

**Workaround**: Being addressed in current parameter-update branch work.

---

### 2. Missing UI Elements Referenced in Callbacks

**Location**: `utils/dash_app.py`

**Problem**: Callbacks reference elements not defined in the layout:
- `Output("param-ui", "children")` - No element with id `param-ui` in layout
- `Output("debug-output", "children")` - No element with id `debug-output` in layout
- `Input("algo-selector", "value")` - No element with id `algo-selector` in layout

**Impact**: Callbacks will fail silently or throw errors at runtime.

---

### 3. Unused Imports

**Locations**:
- `domains_clustering_interactive_plots_dash.py`: `matplotlib.pyplot`, `seaborn`, `StandardScaler`, `TSNE`, `defaultdict` imported but not used
- `utils/functions.py`: `sys` imported but unused
- `utils/dash_app.py`: Some Dash imports may be unused

**Impact**: Minimal, but increases import time and memory.

---

### 4. Type Ignore Comments

**Pattern**: Heavy use of `# type: ignore` for pandas and third-party libraries.

**Example**:
```python
import pandas as pd  # type: ignore
import umap  # type: ignore
```

**Impact**: Type checking disabled for these imports; potential type errors won't be caught.

---

### 5. Embedding File Path Assumptions

**Location**: `utils/functions.py:286-288`

**Issue**: File path formatting uses f-string with unescaped bracket for dict access:
```python
print(f"[SELECTVEC] selectvec file {config["selectvec"]}")
```

**Note**: This is valid Python 3.12+ syntax but may cause issues on older versions.

---

## Potential Edge Cases

### Empty Data Handling
- `extract_text_fields()` filters to `combined_text.str.len() >= 5` - CDEs with very short text are excluded
- Empty DataFrames returned on load errors - caller must check

### Domain Mapping
- CDEs without matching tinyid get "Unknown" domain
- Duplicate tinyids are deduplicated (keeps first)

### Clustering
- HDBSCAN may produce many noise points (label -1) with default parameters
- Silhouette score returns 0.0 if fewer than 2 clusters found

### Parameter Updates
- Parameters are merged with local defaults in `apply_dimensionality_reduction()`:
  ```python
  tsne_local = {...}
  tsne_params.update(tsne_local)  # Local values override config
  ```

---

## Configuration Pitfalls

### INI Parsing
- Multiline values must not have leading spaces on continuation lines
- Boolean values: only "true"/"false" recognized (case-insensitive)
- Tuple/list values require Python literal syntax: `(1, 2, 3)` or `[1, 2, 3]`

### Model Names
- Model names in config must match keys used in embedding file templates
- Case-sensitive matching

---

## Performance Considerations

### Memory
- Large embedding matrices loaded into memory
- Multiple visualization embeddings stored per model
- Analysis results cached in `self.analysis_results` dict

### Startup Time
- All embedding models loaded at startup
- Consider lazy loading for unused models

### Computation
- t-SNE with `method='exact'` is slow for large datasets
- UMAP faster but still significant for >10K points

---

## Template for Future Issues

When discovering new gotchas, document them here:

```markdown
### [Issue Title]

**Location**: [file:line]

**Problem**: [Description]

**Workaround**: [If any]

**Status**: [Open/Resolved/In Progress]
```
