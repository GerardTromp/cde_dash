import dash_bootstrap_components as dbc  # type: ignore
import dash  # type: ignore
import ast
from dash import dcc, html, Input, Output, State  # type: ignore
from typing import Dict, List, Tuple, Optional, Any, Union

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
