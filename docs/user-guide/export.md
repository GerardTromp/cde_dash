# Data Export

The application supports multiple export formats for selected data points and analysis parameters.

## Selecting Data Points

### Using Lasso Selection

1. Click the **lasso** icon in the plot toolbar
2. Draw a shape around the points you want to select
3. Selected points are highlighted

### Using Box Selection

1. Click the **box select** icon in the plot toolbar
2. Draw a rectangle around the points
3. All points within the box are selected

### Selection Info

The selection counter shows how many points are selected:

```
Selected 42 data point(s)
```

## Export Formats

### Export to JSON

Click **Export to JSON** to save structured data:

```json
[
  {
    "tinyid": "CDE12345",
    "cluster": 3,
    "name": "Blood Pressure Measurement",
    "question": "What is the patient's blood pressure?",
    "definition": "Measurement of arterial pressure...",
    "domain": "Cardiovascular",
    "x": 2.345,
    "y": -1.234
  },
  ...
]
```

**Filename format**: `selected_cdes_{model}_{timestamp}.json`

### Export to CSV

Click **Export to CSV** for tabular format:

| tinyid | cluster | name | question | definition | domain | x | y |
|--------|---------|------|----------|------------|--------|---|---|
| CDE12345 | 3 | Blood Pressure... | What is... | Measurement... | Cardiovascular | 2.345 | -1.234 |

**Filename format**: `selected_cdes_{model}_{timestamp}.csv`

### Copy to Clipboard

Click **Copy to Clipboard** for formatted text:

```
Selected CDE Data
==================================================

CDE 1:
  Tiny ID: CDE12345
  Domain: Cardiovascular
  Cluster: 3
  Name: Blood Pressure Measurement
  Question: What is the patient's blood pressure?
  Definition: Measurement of arterial pressure...
  Coordinates: (2.345, -1.234)

CDE 2:
  ...
```

## Parameter Export

Click **Export Parameters (YAML)** to save current analysis configuration:

```yaml
exported_at: '2026-01-18T09:30:00.000000'
model: SAPBERT
dimension_reduction:
  method: umap
  parameters:
    n_neighbors: 15
    min_dist: 0.1
    metric: cosine
clustering:
  method: hdbscan
  parameters:
    min_cluster_size: 15
    min_samples: 5
    metric: euclidean
    cluster_selection_method: eom
```

**Filename format**: `YYYYMMDD-HHMM-params.yaml`

## Export Location

All exported files are saved to the **current working directory** (where you ran the application).

To change the export location:

```bash
cd /path/to/output/directory
python /path/to/domains_clustering_interactive_plots_dash.py
```

## Use Cases

### Cluster Analysis

1. Run analysis with desired parameters
2. Use lasso to select a specific cluster
3. Export to CSV for further analysis in Excel/R

### Comparison Study

1. Run analysis with method A
2. Select interesting points, export to JSON
3. Change method B, re-run
4. Compare which points remain clustered together

### Reproducibility

1. Tune parameters until satisfied
2. Export parameters to YAML
3. Share YAML file with collaborators
4. Load same parameters in future sessions

### Report Generation

1. Select relevant data points
2. Copy to clipboard
3. Paste into report document
4. Add plot screenshot (camera icon in toolbar)
