import dash_bootstrap_components as dbc  # type: ignore
import dash  # type: ignore
import ast
import json
import pandas as pd
import pyperclip  # type: ignore
from dash import dcc, html, callback, Input, Output, State  # type: ignore
import plotly.graph_objects as go  # type: ignore
from typing import Dict, List, Tuple, Optional, Any, Union
from datetime import datetime
from utils.functions import logger

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


def sync_params(self, values, ids):
    for v, id_dict in zip(values, ids):
        algo = id_dict["algo"]
        param = id_dict["param"]
        self.params[algo][param] = auto_cast(v)  # <-- cast before saving
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


def update_plot(self, selected_model):
    """Update plot based on model selection"""
    print(f"Generating plot for {selected_model}...")
    if selected_model not in self.embedding_models:
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text=f"Model '{selected_model}' not available.",
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(size=14, color="red"),
        )
        empty_fig.update_layout(
            title=f"Model Not Available: {selected_model}",
            width=800,
            height=400,
        )
        return empty_fig, selected_model
    if selected_model not in self.analysis_results:
        results = self.run_analysis(selected_model)
        if results:
            self.analysis_results[selected_model] = results
            figures = self.create_faceted_plots(results)
            if figures:
                print(f"Plot generated for {selected_model}")
                return figures[0], selected_model
    if selected_model in self.analysis_results:
        figures = self.create_faceted_plots(self.analysis_results[selected_model])
        if figures:
            print(f"Plot generated for {selected_model}")
            return figures[0], selected_model
    empty_fig = go.Figure()
    empty_fig.add_annotation(
        text="No data available",
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
    )
    print(f"No data for {selected_model}")
    return empty_fig, selected_model


def update_selection_info(selected_data):
    """Update selection info and store data."""
    if not selected_data or not selected_data.get("points"):
        return "No points selected", ""
    points = selected_data["points"]
    selected_data_list = [
        {
            "tinyid": point["customdata"][0],
            "cluster": point["customdata"][1],
            "name": point["customdata"][2],
            "question": point["customdata"][3],
            "definition": point["customdata"][4],
            "domain": point.get("legendgroup", "Unknown"),
            "x": point["x"],
            "y": point["y"],
        }
        for point in points
        if "customdata" in point
    ]
    return f"Selected {len(points)} data point(s)", json.dumps(selected_data_list)


def handle_export(
    self,
    ctx,
    json_clicks,
    csv_clicks,
    clipboard_clicks,
    selected_data_json,
    current_model,
):
    """Handle data export."""
    # ctx = callback_context
    if not ctx.triggered or not selected_data_json:
        return dbc.Alert("No data selected", color="warning")
    try:
        selected_data = json.loads(selected_data_json)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if ctx.triggered[0]["prop_id"].split(".")[0] == "export-json-btn":
            filename = f"selected_cdes_{current_model}_{timestamp}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(selected_data, f, indent=2, ensure_ascii=False)
            return dbc.Alert(f"Data exported to {filename}", color="success")
        elif ctx.triggered[0]["prop_id"].split(".")[0] == "export-csv-btn":
            filename = f"selected_cdes_{current_model}_{timestamp}.csv"
            pd.DataFrame(selected_data).to_csv(filename, index=False, encoding="utf-8")
            return dbc.Alert(f"Data exported to {filename}", color="success")
        elif ctx.triggered[0]["prop_id"].split(".")[0] == "copy-clipboard-btn":
            pyperclip.copy(self._format_clipboard_data(selected_data))
            return dbc.Alert("Data copied to clipboard", color="success")
    except Exception as e:
        logger.error(f"Export error: {e}")
        return dbc.Alert(f"Export failed: {str(e)}", color="danger")
    return ""
