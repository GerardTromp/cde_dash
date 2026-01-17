# Patterns & Conventions

## Design Patterns

### 1. Method Delegation Pattern

The `InteractiveClusteringAnalyzer` class imports methods from utility modules and assigns them as class attributes:

```python
# In domains_clustering_interactive_plots_dash.py
class InteractiveClusteringAnalyzer:
    load_domain_mapping = load_domain_mapping  # from utils.functions
    extract_text_fields = extract_text_fields
    run_analysis = run_analysis                # from utils.run_analysis
    # ... etc
```

**Purpose**: Keeps main class compact while distributing logic across focused modules.

**Convention**: Methods are defined with `self` as first parameter in their source modules, allowing them to work as instance methods when assigned to the class.

### 2. Configuration-Driven Behavior

Application behavior is controlled by INI configuration files:

```python
config = load_configs(path=args.config_path)
analyzer.config = config
analyzer.umap_params = params["UMAP"]
```

**Convention**: Configs are loaded once at startup and stored on the analyzer instance.

### 3. Callback Registration Pattern (Dash)

Callbacks are registered inside a method using inner functions:

```python
def setup_callbacks(self):
    @self.app.callback(...)
    def update_plot(selected_model):
        # Can access self.embedding_models, etc.
        ...
```

**Purpose**: Allows callbacks to access analyzer state via closure over `self`.

### 4. Graceful Fallback Pattern

Data loading functions return empty containers on failure:

```python
def load_cde_data(self, file_path):
    try:
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        print(f"Error loading CDE data: {e}")
        logger.error(f"Error loading CDE data: {e}")
        return pd.DataFrame()  # Empty DataFrame on failure
```

### 5. Memoization Pattern

Analysis results are cached to avoid recomputation:

```python
if selected_model not in self.analysis_results:
    results = self.run_analysis(selected_model)
    self.analysis_results[selected_model] = results
# Use cached results on subsequent calls
```

## Coding Conventions

### Naming
- **Classes**: PascalCase (`InteractiveClusteringAnalyzer`)
- **Functions**: snake_case (`load_domain_mapping`, `run_analysis`)
- **Private Methods**: Leading underscore (`_truncate_text`, `_clean_text`)
- **Constants**: Lists defined inline in class `__init__`

### Type Hints
Partial adoption:
```python
def apply_dimensionality_reduction(
    self, embeddings: np.ndarray, method: str = "tsne"
) -> np.ndarray:
```

Type ignore comments used for pandas:
```python
import pandas as pd  # type: ignore
```

### Logging
Dual logging setup:
- Console: WARNING and above
- File: DEBUG and above to `interactive_clustering.log`

```python
logger.info(f"Loading domain mapping from {file_path}")
logger.error(f"Error loading CDE data: {e}")
```

### Print Statements
Used alongside logging for user feedback:
```python
print(f"Loaded {len(domain_df)} domain mappings")
logger.info(f"Loaded {len(domain_df)} mappings")
```

### Error Handling
Comprehensive exception catching with specific handlers:
```python
except FileNotFoundError:
    print(f"Error: The file '{filepath}' was not found.")
    return None
except PermissionError:
    print(f"Error: Permission denied for '{filepath}'.")
    return None
except IOError as e:
    print(f"An I/O error occurred: {e}")
    return None
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    return None
```

### Formatting
- Black-style formatting with `# fmt: off` / `# fmt: on` for manual control
- Used for D3 color lists and Dash layout blocks

## Testing Patterns

**No formal test suite identified.**

Current testing approach:
- Manual testing via Dash web interface
- Print statements for debugging
- Logging to file for troubleshooting

## File Organization

### Import Order
1. Standard library
2. Third-party packages
3. Local imports (utils.*)

### Module Responsibility
| Module | Responsibility |
|--------|----------------|
| `functions.py` | Data I/O, configuration |
| `run_analysis.py` | ML pipeline |
| `dash_app.py` | Web interface |
| `dash_app_functions.py` | UI component builders |
| `internal_functions.py` | Helpers (text, plotting) |
| `argparse.py` | CLI interface |

## Parameter Handling

### INI to Dict Conversion
Custom parsing with type inference:
```python
def config_to_dict(configuration) -> Dict:
    # Handles: lists (newline-separated), bools, ints, floats, tuples, None
```

### Dynamic Type Casting
```python
def auto_cast(val):
    # Attempts: literal_eval, bool, infinity, int, float, fallback to string
```
