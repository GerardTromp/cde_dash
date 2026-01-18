import dash_bootstrap_components as dbc  # type: ignore
import dash  # type: ignore
import ast
from dash import dcc, html, Input, Output, State  # type: ignore
from typing import Dict, List, Tuple, Optional, Any, Union

# CSS styles for tiered parameter sections
TIER_STYLES = {
    "tier2_button": {
        "fontSize": "0.85rem",
        "padding": "0.25rem 0.5rem",
        "marginTop": "0.5rem",
        "marginBottom": "0.25rem",
    },
    "tier3_button": {
        "fontSize": "0.8rem",
        "padding": "0.2rem 0.4rem",
        "marginTop": "0.25rem",
        "marginBottom": "0.25rem",
    },
    "tier_section": {
        "paddingLeft": "0.5rem",
        "borderLeft": "2px solid #dee2e6",
        "marginTop": "0.5rem",
    },
    "highlight": {
        "border": "2px solid #fd7e14",
        "borderRadius": "4px",
        "padding": "0.25rem",
    },
}

# Initial parameter sets
# param_sets = {
#     "UMAP": {"n_neighbors": 15, "min_dist": 0.1, "metric": "euclidean"},
#     "tSNE": {"perplexity": 30, "learning_rate": 200, "n_iter": 1000}
# }

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


# --- Helper: safe type conversion ---
def auto_cast(val):
    if val is None or val == "":
        return None
    if isinstance(val, str):
        v = val.strip()

        # --- Try literal_eval for tuple/list/dict/None ---
        if (v.startswith("(") and v.endswith(")")) or (
            v.startswith("[") and v.endswith("]")
        ):
            try:
                return ast.literal_eval(v)
            except Exception:
                pass  # fall back if it isn’t valid Python literal

        # --- booleans ---
        if v.lower() in ("true", "false"):
            return v.lower() == "true"

        # --- infinity ---
        if v.lower() in ("inf", "infinity", "-inf"):
            return float(v)

        # --- numbers ---
        try:
            return int(v)
        except ValueError:
            pass
        try:
            return float(v)
        except ValueError:
            pass

        # --- fallback string ---
        return v
    return val


# --- UI builder for parameter cards ---
def param_inputs(params: dict, algo_name: str):
    rows = []
    for k, v in params.items():
        # --- Always stringify for Dash ---
        if v is None or v is bool:
            display_val = ""  # empty box instead of "None"
        elif isinstance(v, (list, tuple)):
            display_val = str(v)  # e.g. "(1, 2, None)"
        else:
            display_val = str(v)  # force into string

        rows.append(
            dbc.Row(
                [
                    dbc.Col(html.Label(k, htmlFor=f"{algo_name}-{k}"), width=3),
                    dbc.Col(
                        dcc.Input(
                            id={"type": "param-input", "algo": algo_name, "param": k},
                            value=display_val,
                            type="text",
                            className="form-control",
                        ),
                        width=9,
                    ),
                ],
                className="mb-2",
            )
        )
    return dbc.Card([dbc.CardHeader(algo_name), dbc.CardBody(rows)], className="mb-3")


# --- Layout ---
# app.layout = dbc.Container(
#     [
#         html.H2("Parameter Configuration"),
#         dcc.Dropdown(
#             id="algo-selector",
#             options=[{"label": k, "value": k} for k in param_sets.keys()],
#             value=["UMAP"],
#             multi=True,
#         ),
#         html.Div(id="param-ui"),
#         html.Hr(),
#         dbc.Button("Show Current Params", id="show-btn", className="mb-3"),
#         html.Pre(id="debug-output"),
#     ],
#     fluid=True,
# )


# # --- Callback: render parameter UIs ---
# @self.app.callback(Output("param-ui", "children"), Input("algo-selector", "value"))
# def update_params(algos):
#     if not algos:
#         return []
#     return [param_inputs(param_sets[a], a) for a in algos]


# # --- Callback: update param_sets on any input change ---
# @self.app.callback(
#     self,
#     Output("debug-output", "children"),
#     Input({"type": "param-input", "algo": dash.ALL, "param": dash.ALL}, "value"),
#     State({"type": "param-input", "algo": dash.ALL, "param": dash.ALL}, "id"),
#     prevent_initial_call=True,
# )


def sync_params(self, values, ids):
    for v, id_dict in zip(values, ids):
        algo = id_dict["algo"]
        param = id_dict["param"]
        self.param_sets[algo][param] = auto_cast(v)  # <-- cast before saving
    return f"Updated Params:\n{self.param_sets}"


def _is_float_string(s) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


def config_to_dict(configuration) -> Dict:
    config_dict = {}
    for section in configuration.sections():
        config_dict[section] = {}
        for option in configuration.options(section):

            value = configuration.get(section, option).lstrip()

            if "\n" in value:
                # print(f"Match for section: {section}, option: {option}, value: {value}\n")
                config_dict[section][option] = [
                    item.strip() for item in value.splitlines() if item.strip()
                ]
            elif value.lower() in ("true", "false"):
                config_dict[section][option] = configuration.getboolean(section, option)
            elif value.isdigit():
                config_dict[section][option] = configuration.getint(section, option)
            elif _is_float_string(value):
                # print(f"Match for section: {section}, option: {option}, value: {value}\n")
                config_dict[section][option] = configuration.getfloat(section, option)
            elif "(" in value:
                value = ast.literal_eval(value)
                config_dict[section][option] = value
            elif "None" in value:
                value = None
                config_dict[section][option] = value
            else:
                config_dict[section][option] = value

    return config_dict


def param_inputs_from_schema(
    schema: Dict[str, Dict[str, Any]], method_id: str, current_params: Dict[str, Any]
) -> dbc.Card:
    """Build parameter input card from a method's schema.

    Args:
        schema: Parameter schema from method.param_schema()
        method_id: Method identifier (e.g., "umap")
        current_params: Current parameter values

    Returns:
        A dbc.Card containing labeled input fields for each parameter
    """
    rows = []
    for param_name, spec in schema.items():
        param_type = spec.get("type", "text")
        default = spec.get("default")
        description = spec.get("description", param_name)
        current_value = current_params.get(param_name, default)

        input_id = {"type": "param-input", "algo": method_id, "param": param_name}

        if param_type == "select":
            # Dropdown for select type
            options: List[Dict[str, Any]] = [
                {"label": str(opt), "value": opt} for opt in spec.get("options", [])
            ]
            input_element = dcc.Dropdown(
                id=input_id,
                options=options,  # type: ignore[arg-type]
                value=current_value,
                clearable=False,
                className="form-control",
            )
        elif param_type == "bool":
            # Checkbox for boolean
            input_element = dbc.Switch(
                id=input_id,
                value=bool(current_value),
                className="mt-1",
            )
        elif param_type == "int":
            # Number input for integers
            input_element = dcc.Input(
                id=input_id,
                value=current_value,
                type="number",
                min=spec.get("min"),
                max=spec.get("max"),
                step=spec.get("step", 1),
                className="form-control",
            )
        elif param_type == "float":
            # Number input for floats
            input_element = dcc.Input(
                id=input_id,
                value=current_value,
                type="number",
                min=spec.get("min"),
                max=spec.get("max"),
                step=spec.get("step", 0.01),
                className="form-control",
            )
        else:
            # Text input as fallback
            input_element = dcc.Input(
                id=input_id,
                value=str(current_value) if current_value is not None else "",
                type="text",
                className="form-control",
            )

        rows.append(
            dbc.Row(
                [
                    dbc.Col(
                        html.Label(
                            param_name,
                            htmlFor=f"{method_id}-{param_name}",
                            title=description,
                        ),
                        width=4,
                    ),
                    dbc.Col(input_element, width=8),
                ],
                className="mb-2",
            )
        )

    return dbc.Card([dbc.CardBody(rows)], className="mt-2")


def _create_param_row(
    param_name: str,
    spec: Dict[str, Any],
    method_id: str,
    current_value: Any,
    category: str = "dim_reduction",
) -> dbc.Row:
    """Create a single parameter input row.

    Args:
        param_name: Name of the parameter
        spec: Parameter specification from schema
        method_id: Method identifier (e.g., "umap")
        current_value: Current parameter value
        category: "dim_reduction" or "clustering"

    Returns:
        A dbc.Row with label and input control
    """
    param_type = spec.get("type", "text")
    description = spec.get("description", param_name)
    is_highlighted = spec.get("highlight", False)

    # Use pattern-matching ID structure
    input_id = {
        "type": f"{category}-param",
        "algorithm": method_id,
        "param": param_name,
    }

    if param_type == "select":
        options: List[Dict[str, Any]] = [
            {"label": str(opt), "value": opt} for opt in spec.get("options", [])
        ]
        input_element = dcc.Dropdown(
            id=input_id,
            options=options,  # type: ignore[arg-type]
            value=current_value,
            clearable=False,
            className="form-control",
        )
    elif param_type == "bool":
        input_element = dbc.Switch(
            id=input_id,
            value=bool(current_value),
            className="mt-1",
        )
    elif param_type == "int":
        input_element = dcc.Input(
            id=input_id,
            value=current_value,
            type="number",
            min=spec.get("min"),
            max=spec.get("max"),
            step=spec.get("step", 1),
            className="form-control",
        )
    elif param_type == "float":
        input_element = dcc.Input(
            id=input_id,
            value=current_value,
            type="number",
            min=spec.get("min"),
            max=spec.get("max"),
            step=spec.get("step", 0.01),
            className="form-control",
        )
    else:
        input_element = dcc.Input(
            id=input_id,
            value=str(current_value) if current_value is not None else "",
            type="text",
            className="form-control",
        )

    # Apply highlight style if flagged
    row_style = TIER_STYLES["highlight"] if is_highlighted else {}

    return dbc.Row(
        [
            dbc.Col(
                html.Label(
                    param_name,
                    htmlFor=f"{method_id}-{param_name}",
                    title=description,
                ),
                width=4,
            ),
            dbc.Col(input_element, width=8),
        ],
        className="mb-2",
        style=row_style,
    )


def create_tiered_param_section(
    schema: Dict[str, Dict[str, Any]],
    method_id: str,
    current_params: Dict[str, Any],
    category: str = "dim_reduction",
) -> html.Div:
    """Build a tiered parameter section with collapsible tiers.

    Creates a three-tier collapsible UI:
    - Tier 1 (Essential): Always visible
    - Tier 2 (Important): Collapsible, revealed by "More options" button
    - Tier 3 (Advanced): Nested collapsible within Tier 2

    Args:
        schema: Parameter schema from method.param_schema()
        method_id: Method identifier (e.g., "umap", "hdbscan")
        current_params: Current parameter values
        category: "dim_reduction" or "clustering" (for ID namespacing)

    Returns:
        An html.Div containing the tiered parameter UI
    """
    # Group parameters by tier
    tier1_params: List[Tuple[str, Dict[str, Any]]] = []
    tier2_params: List[Tuple[str, Dict[str, Any]]] = []
    tier3_params: List[Tuple[str, Dict[str, Any]]] = []

    for param_name, spec in schema.items():
        tier = spec.get("tier", 1)
        if tier == 1:
            tier1_params.append((param_name, spec))
        elif tier == 2:
            tier2_params.append((param_name, spec))
        else:
            tier3_params.append((param_name, spec))

    # Build Tier 1 rows (always visible)
    tier1_rows = [
        _create_param_row(
            name, spec, method_id, current_params.get(name, spec.get("default")), category
        )
        for name, spec in tier1_params
    ]

    # Build Tier 3 rows (nested inside Tier 2)
    tier3_rows = [
        _create_param_row(
            name, spec, method_id, current_params.get(name, spec.get("default")), category
        )
        for name, spec in tier3_params
    ]

    # Build Tier 2 rows (includes Tier 3 nested collapse)
    tier2_rows = [
        _create_param_row(
            name, spec, method_id, current_params.get(name, spec.get("default")), category
        )
        for name, spec in tier2_params
    ]

    # Tier 3 collapse (nested within Tier 2)
    tier3_section = []
    if tier3_params:
        tier3_collapse_id = f"{category}-{method_id}-tier3-collapse"
        tier3_button_id = f"{category}-{method_id}-tier3-toggle"
        tier3_section = [
            dbc.Button(
                "▸ Advanced",
                id=tier3_button_id,
                size="sm",
                outline=True,
                color="secondary",
                style=TIER_STYLES["tier3_button"],
            ),
            dbc.Collapse(
                html.Div(tier3_rows, style=TIER_STYLES["tier_section"]),
                id=tier3_collapse_id,
                is_open=False,
            ),
        ]

    # Tier 2 collapse (includes Tier 3 nested)
    tier2_section = []
    if tier2_params or tier3_params:
        tier2_collapse_id = f"{category}-{method_id}-tier2-collapse"
        tier2_button_id = f"{category}-{method_id}-tier2-toggle"
        tier2_section = [
            dbc.Button(
                "▸ More options",
                id=tier2_button_id,
                size="sm",
                outline=True,
                color="secondary",
                style=TIER_STYLES["tier2_button"],
            ),
            dbc.Collapse(
                html.Div(
                    tier2_rows + tier3_section,
                    style=TIER_STYLES["tier_section"],
                ),
                id=tier2_collapse_id,
                is_open=False,
            ),
        ]

    # Combine all tiers
    return html.Div(tier1_rows + tier2_section)


def get_tier_collapse_ids(
    method_id: str, category: str = "dim_reduction"
) -> Dict[str, Dict[str, str]]:
    """Get the collapse and button IDs for a method's tiered sections.

    Used by callbacks to wire up collapse/expand behavior.

    Args:
        method_id: Method identifier (e.g., "umap", "hdbscan")
        category: "dim_reduction" or "clustering"

    Returns:
        Dict with "tier2" and "tier3" keys, each containing
        "collapse" and "button" ID strings
    """
    return {
        "tier2": {
            "collapse": f"{category}-{method_id}-tier2-collapse",
            "button": f"{category}-{method_id}-tier2-toggle",
        },
        "tier3": {
            "collapse": f"{category}-{method_id}-tier3-collapse",
            "button": f"{category}-{method_id}-tier3-toggle",
        },
    }


def get_toggle_button_text(is_open: bool, tier: int) -> str:
    """Get the text for a tier toggle button based on state.

    Args:
        is_open: Whether the collapse is currently open
        tier: Tier level (2 or 3)

    Returns:
        Button text with appropriate arrow indicator
    """
    if tier == 2:
        return "▾ More options" if is_open else "▸ More options"
    else:  # tier 3
        return "▾ Advanced" if is_open else "▸ Advanced"
