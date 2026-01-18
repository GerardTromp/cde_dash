# Parameter UI Expansion - Phased Implementation Plan

**Created**: 2026-01-18
**Status**: Phase 6 Complete - Feature Complete
**Last Commit**: `6d2b2b4` (Phase 6)
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

### Phase 1: Schema Extension (Foundation) ✅ COMPLETE
**Scope**: Extend method schemas to support tiered parameters
**Files**: `utils/methods/base.py`, all method files in `dim_reduction/` and `clustering/`
**Commit**: `9d87d18`

Tasks:
- [x] Add `tier` field to parameter schema (1=Essential, 2=Important, 3=Advanced)
- [x] Update existing method schemas with tier assignments
- [x] Add any missing parameters from wireframe definitions
- [x] Add `highlight` field for emphasized parameters

**Checkpoint**: Can be compacted after Phase 1

---

### Phase 2: Collapsible UI Components ✅ COMPLETE
**Scope**: Create collapsible parameter group components
**Files**: `utils/dash_app_functions.py`

Tasks:
- [x] Create `create_tiered_param_section()` function
- [x] Implement `dbc.Collapse` wrappers for Tier 2 and Tier 3
- [x] Add toggle buttons/banners for expand/collapse
- [x] Style collapsed vs expanded states

**Added Functions**:
- `_create_param_row()` - Creates single parameter input row with highlight support
- `create_tiered_param_section()` - Main tiered UI builder with nested collapses
- `get_tier_collapse_ids()` - Returns IDs for callback wiring
- `get_toggle_button_text()` - Returns toggle button text based on state
- `TIER_STYLES` - CSS styles dict for tier UI elements

**Checkpoint**: Can be compacted after Phase 2

---

### Phase 3: Update Layout for Tiered Display ✅ COMPLETE
**Scope**: Integrate tiered parameters into main layout
**Files**: `utils/dash_app.py`, `utils/dash_app_functions.py`

Tasks:
- [x] Update imports in `dash_app.py` for new tiered functions
- [x] Modify `update_dim_params()` callback to use `create_tiered_param_section()`
- [x] Modify `update_clustering_params()` callback to use `create_tiered_param_section()`
- [x] Split `sync_params()` into separate callbacks for dim_reduction and clustering
- [x] Update pattern-matching IDs from `param-input`/`algo` to `{category}-param`/`algorithm`

**Changes Made**:
- Updated imports to include `create_tiered_param_section`, `get_tier_collapse_ids`, `get_toggle_button_text`
- Both param rendering callbacks now use `create_tiered_param_section()` with appropriate category
- Created separate sync callbacks: `sync_dim_params()` and `sync_cluster_params()`
- ID structure now uses `{"type": "dim_reduction-param", "algorithm": ..., "param": ...}`

**Checkpoint**: Can be compacted after Phase 3

---

### Phase 4: Collapse/Expand Callbacks ✅ COMPLETE
**Scope**: Wire up interactivity for collapsible sections
**Files**: `utils/dash_app.py`, `utils/dash_app_functions.py`

Tasks:
- [x] Add callbacks for Tier 2 toggle buttons
- [x] Add callbacks for Tier 3 toggle buttons (nested)
- [x] Convert tier button/collapse IDs to pattern-matching format for MATCH callbacks

**Changes Made**:
- Imported `MATCH` from dash in `dash_app.py`
- Updated `create_tiered_param_section()` to use pattern-matching IDs:
  - Button IDs: `{"type": "{category}-tier-toggle", "tier": 2|3, "algorithm": method_id}`
  - Collapse IDs: `{"type": "{category}-tier-collapse", "tier": 2|3, "algorithm": method_id}`
- Updated `get_tier_collapse_ids()` to return pattern-matching ID dicts
- Added 4 callbacks using `MATCH` for collapse/expand:
  - `toggle_dim_tier2()` - Tier 2 for dim_reduction
  - `toggle_dim_tier3()` - Tier 3 for dim_reduction
  - `toggle_cluster_tier2()` - Tier 2 for clustering
  - `toggle_cluster_tier3()` - Tier 3 for clustering
- Callbacks update both collapse state and button text (arrow indicator)

**Checkpoint**: Can be compacted after Phase 4

---

### Phase 5: Second Clustering Method ✅ COMPLETE
**Scope**: Add second clustering method selector with parameters
**Files**: `utils/dash_app.py`, `utils/run_analysis.py`

Tasks:
- [x] Add second clustering method dropdown
- [x] Add parameter section for second clustering method
- [x] Update analysis pipeline to support two clustering methods
- [x] Update plot functions for dual clustering display

**Changes Made**:
- Added `clustering-compare-toggle` switch and `clustering-selector-2` dropdown to layout
- Added `clustering-params-2` div for secondary clustering parameters
- Added `toggle_clustering_comparison()` callback to show/hide secondary clustering UI
- Added `update_clustering_params_2()` callback to render secondary clustering parameters
- Updated `run_selected_analysis()` callback to accept `cluster_compare_mode` and `cluster_method_2` states
- Added logic to prioritize dim_compare > cluster_compare > single mode
- Created `create_clustering_comparison_plot()` in `run_analysis.py` for dual clustering visualization
- Existing pattern-matching callbacks already handle secondary clustering (same `clustering-param` type)

**Checkpoint**: Can be compacted after Phase 5

---

### Phase 6: Integration & Testing ✅ COMPLETE
**Scope**: Full integration and verification
**Files**: Multiple

Tasks:
- [x] End-to-end testing with all method combinations
- [x] Verify parameter collection works correctly
- [x] Test collapse/expand behavior
- [x] Fix any callback conflicts

**Bug Fixed**:
- Added missing `create_clustering_comparison_plot` import and class assignment in `domains_clustering_interactive_plots_dash.py`

**Tests Performed**:
- Module imports and method registry validation
- Tiered parameter UI generation for all 7 methods (3 dim reduction, 4 clustering)
- Pattern-matching callback registration verification
- Auto-cast function validation
- Dash app creation with 16 registered callbacks

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
