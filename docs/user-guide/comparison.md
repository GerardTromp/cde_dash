# Comparison Mode

Comparison mode allows you to visualize two dimension reduction methods side-by-side to validate your analysis.

## Enabling Comparison Mode

1. Toggle **"Compare two dimension reduction methods"** switch
2. A secondary dropdown appears
3. Select a different method

## What Gets Compared

- **Same embeddings** are used for both methods
- **Same clustering** is applied to each reduced space
- Results may differ because clustering operates on different 2D representations

## Interface

When comparison mode is enabled:

```
┌────────────────────────────┬────────────────────────────┐
│       UMAP + HDBSCAN       │      t-SNE + HDBSCAN       │
│   Clusters: 12             │   Clusters: 14             │
│   Silhouette: 0.432        │   Silhouette: 0.389        │
├────────────────────────────┼────────────────────────────┤
│                            │                            │
│       [UMAP Plot]          │      [t-SNE Plot]          │
│                            │                            │
└────────────────────────────┴────────────────────────────┘
```

Both plots:

- Share the same color scheme (by domain)
- Have synchronized legends
- Support independent hover/zoom

## Use Cases

### Validate Cluster Structure

If clusters appear in **both** UMAP and t-SNE, they likely represent real structure in the data.

If clusters only appear in one method, they may be artifacts.

### Compare Methods for Your Data

- UMAP tends to preserve global relationships
- t-SNE emphasizes local neighborhoods
- PCA provides linear baseline

See which method better separates your domains.

### Parameter Sensitivity

Compare:

- UMAP (n_neighbors=10) vs UMAP (n_neighbors=50)
- t-SNE (perplexity=15) vs t-SNE (perplexity=50)

Note: You'd need to run single mode twice for same-method comparison.

## Interpretation Tips

### Consistent Clusters

Points that cluster together in **both** plots:

- Strong evidence of real similarity
- Good candidates for merging/grouping

### Method-Specific Clusters

Points clustered in one plot but not the other:

- May indicate density variations
- Check if one method's parameters need tuning
- Consider which method is more appropriate for your analysis

### Noise Differences

Different noise point counts between methods:

- Normal - methods have different density estimation
- Very different counts may indicate parameter issues

## Limitations

- Both methods use the **same clustering algorithm**
- Only dimension reduction methods can be compared
- Parameters for secondary method use defaults
- Secondary method parameter panel not shown (use first method settings as guide)

## Best Practices

1. **Start without comparison** - tune one method first
2. **Enable comparison** to validate findings
3. **Export parameters** when satisfied with primary method
4. **Consider multiple comparisons** if results differ significantly

## Example Workflow

1. Run UMAP + HDBSCAN analysis
2. Identify interesting clusters
3. Enable comparison with t-SNE
4. Check if same points cluster together
5. If consistent → clusters are robust
6. If different → investigate why (parameters, data structure)
