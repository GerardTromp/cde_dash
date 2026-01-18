# Parameter UI Expansion - Phased Implementation Plan

**Created**: 2026-01-18
**Status**: Planning
**Reference**: `../Claude_WireframeDescription.md`, `../Wireframe_clusterAppMethodsParameters.zip`

## Overview

Expand the parameter section with:
1. Collapsible/expandable parameter groups (tiered by influence)
2. Second clustering method with adjustable parameters
3. Tiered parameter display (Essential → Important → Advanced)

## Wireframe Reference

The wireframe from a separate Claude session provides:
- `app.py` - Full Dash app with tiered collapse UI
- `params_definitions.py` - Parameter definitions with tier classifications
- Pattern-matching callback IDs: `{"type": "{category}-param", "algorithm": "{name}", "param": "{param}"}`

## Phased Implementation

### Phase 1: Schema Extension (Foundation)
**Scope**: Extend method schemas to support tiered parameters
**Files**: `utils/methods/base.py`, all method files in `dim_reduction/` and `clustering/`

Tasks:
- [ ] Add `tier` field to parameter schema (1=Essential, 2=Important, 3=Advanced)
- [ ] Update existing method schemas with tier assignments
- [ ] Add any missing parameters from wireframe definitions

**Checkpoint**: Can be compacted after Phase 1

---

### Phase 2: Collapsible UI Components
**Scope**: Create collapsible parameter group components
**Files**: `utils/dash_app_functions.py`

Tasks:
- [ ] Create `create_tiered_param_section()` function
- [ ] Implement `dbc.Collapse` wrappers for Tier 2 and Tier 3
- [ ] Add toggle buttons/banners for expand/collapse
- [ ] Style collapsed vs expanded states

**Checkpoint**: Can be compacted after Phase 2

---

### Phase 3: Update Layout for Tiered Display
**Scope**: Integrate tiered parameters into main layout
**Files**: `utils/dash_app.py`, `utils/dash_app_functions.py`

Tasks:
- [ ] Refactor `param_inputs_from_schema()` to support tiers
- [ ] Update layout to use new tiered components
- [ ] Ensure dynamic ID generation works with tiers

**Checkpoint**: Can be compacted after Phase 3

---

### Phase 4: Collapse/Expand Callbacks
**Scope**: Wire up interactivity for collapsible sections
**Files**: `utils/dash_app.py`

Tasks:
- [ ] Add callbacks for Tier 2 toggle buttons
- [ ] Add callbacks for Tier 3 toggle buttons (nested)
- [ ] Handle state preservation across method changes

**Checkpoint**: Can be compacted after Phase 4

---

### Phase 5: Second Clustering Method
**Scope**: Add second clustering method selector with parameters
**Files**: `utils/dash_app.py`, `utils/dash_app_functions.py`, `utils/run_analysis.py`

Tasks:
- [ ] Add second clustering method dropdown
- [ ] Add parameter section for second clustering method
- [ ] Update analysis pipeline to support two clustering methods
- [ ] Update plot functions for dual clustering display

**Checkpoint**: Can be compacted after Phase 5

---

### Phase 6: Integration & Testing
**Scope**: Full integration and verification
**Files**: Multiple

Tasks:
- [ ] End-to-end testing with all method combinations
- [ ] Verify parameter collection works correctly
- [ ] Test collapse/expand behavior
- [ ] Fix any callback conflicts

**Final Checkpoint**: Feature complete

---

## Parameter Tier Assignments (from Wireframe)

### Dimension Reduction

| Method | Tier 1 (Essential) | Tier 2 (Important) | Tier 3 (Advanced) |
|--------|-------------------|-------------------|------------------|
| **PCA** | n_components | whiten, svd_solver | tol, random_state, iterated_power |
| **t-SNE** | n_components, perplexity | learning_rate, n_iter, early_exaggeration | metric, init, method, angle, random_state |
| **UMAP** | n_components, n_neighbors, min_dist | metric, spread, learning_rate | random_state, init, n_epochs, negative_sample_rate |

### Clustering

| Method | Tier 1 (Essential) | Tier 2 (Important) | Tier 3 (Advanced) |
|--------|-------------------|-------------------|------------------|
| **HDBSCAN** | min_cluster_size, min_samples | cluster_selection_method, cluster_selection_epsilon | metric, alpha, algorithm, leaf_size |
| **DBSCAN** | eps, min_samples | metric, algorithm | leaf_size, p, n_jobs |
| **K-Means** | n_clusters | init, n_init | max_iter, tol, random_state, algorithm |
| **Spectral** | n_clusters | affinity, assign_labels | n_neighbors, gamma, random_state |

## Notes

- Use `cluster_selection_method='leaf'` as highlighted option for HDBSCAN (better for many small clusters)
- Consider adding OPTICS and BIRCH methods (recommended in wireframe for many small clusters)
- Pattern-matching callbacks may need adjustment for new ID structure

## Recovery Instructions

After `/compact`, restore context with:
```bash
source .claude/init_session.sh
```

Then read this file and the most recent checkpoint to resume work.
