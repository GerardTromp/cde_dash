import dash  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import json
import pandas as pd  # type: ignore
import numpy as np
import pyperclip  # type: ignore
import plotly.graph_objects as go  # type: ignore
from dash import dcc, html, Input, Output, State, callback_context, MATCH  # type: ignore
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from utils.functions import logger
from utils.dash_app_functions import (
    param_inputs,
    param_inputs_from_schema,
    create_tiered_param_section,
    get_tier_collapse_ids,
    get_toggle_button_text,
)
from utils.methods import MethodRegistry
from utils.export_params import export_params_yaml


def create_dash_app(self) -> dash.Dash:
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    # Build model selection options
    models = self.embedding_models.keys()
    model_options = [{"label": model, "value": model} for model in models]
    value_option = model_options[0]["value"] if model_options else None

    # Build dimension reduction and clustering options from registry
    dim_options = [
        {"label": name, "value": mid}
        for mid, name in MethodRegistry.list_dim_reduction().items()
    ]
    cluster_options = [
        {"label": name, "value": mid}
        for mid, name in MethodRegistry.list_clustering().items()
    ]

    app.layout = dbc.Container(
        [
            # Header
            dbc.Row([
                dbc.Col([
                    html.H1("Interactive CDE Clustering Analysis", className="text-center mb-4"),
                    html.Hr(),
                ])
            ]),
            # Model Selection
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Embedding Model Selection"),
                        dbc.CardBody([
                            dbc.RadioItems(
                                id="model-selector",
                                options=model_options,
                                value=value_option,
                                inline=True,
                            ),
                            html.Div(id="model-status", className="mt-2"),
                        ]),
                    ])
                ])
            ], className="mb-4"),
            # Method Selection: Dimension Reduction and Clustering side-by-side
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Dimension Reduction"),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id="dim-reduction-selector",
                                options=dim_options,
                                value="umap",
                                clearable=False,
                                className="mb-3",
                            ),
                            html.Div(id="dim-reduction-params"),
                        ]),
                    ])
                ], width=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Clustering"),
                        dbc.CardBody([
                            dcc.Dropdown(
                                id="clustering-selector",
                                options=cluster_options,
                                value="hdbscan",
                                clearable=False,
                                className="mb-3",
                            ),
                            html.Div(id="clustering-params"),
                        ]),
                    ])
                ], width=6),
            ], className="mb-4"),
            # Comparison Mode Toggle
            dbc.Row([
                dbc.Col([
                    dbc.Switch(
                        id="comparison-mode-toggle",
                        label="Compare two dimension reduction methods",
                        value=False,
                        className="mb-2",
                    ),
                    html.Div(
                        id="secondary-dim-reduction-container",
                        style={"display": "none"},
                        children=[
                            dbc.Label("Secondary Method:"),
                            dcc.Dropdown(
                                id="dim-reduction-selector-2",
                                options=dim_options,
                                value="tsne",
                                clearable=False,
                                className="mt-2",
                            ),
                        ],
                    ),
                ])
            ], className="mb-2"),
            # Action Row
            dbc.Row([
                dbc.Col([
                    dbc.Button(
                        "Run Analysis",
                        id="run-analysis-btn",
                        color="primary",
                        className="me-2",
                    ),
                    dbc.Button(
                        "Export Parameters (YAML)",
                        id="export-params-btn",
                        color="secondary",
                    ),
                    html.Div(id="param-sync-status", className="mt-2"),
                ])
            ], className="mb-4"),
            # Visualization
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Interactive Clustering Visualization"),
                        dbc.CardBody([
                            dcc.Graph(
                                id="clustering-plot",
                                style={"height": "700px"},
                                config={
                                    "displayModeBar": True,
                                    "modeBarButtonsToAdd": ["select2d", "lasso2d", "resetScale2d"],
                                    "displaylogo": False,
                                },
                            )
                        ]),
                    ])
                ])
            ], className="mb-4"),
            # Data Export
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardHeader("Data Export"),
                        dbc.CardBody([
                            dbc.Row([
                                dbc.Col([
                                    html.P("Select data points using lasso or box selection tools above, then export:"),
                                    html.Div(id="selection-info", className="mb-3"),
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    dbc.Button("Export to JSON", id="export-json-btn", color="primary", className="me-2"),
                                    dbc.Button("Export to CSV", id="export-csv-btn", color="success", className="me-2"),
                                    dbc.Button("Copy to Clipboard", id="copy-clipboard-btn", color="info"),
                                ])
                            ]),
                            dbc.Row([
                                dbc.Col([
                                    html.Div(id="export-status", className="mt-3"),
                                ])
                            ]),
                        ]),
                    ])
                ])
            ]),
            # Hidden stores
            html.Div(id="selected-data-store", style={"display": "none"}),
            html.Div(id="current-model-store", style={"display": "none"}),
        ],
        fluid=True,
    )
    self.app = app
    return app


def setup_callbacks(self):
    """Setup Dash callbacks"""
    if not self.app:
        logger.error("Dash app not initialized")
        return

    # --- Callback: update model status badge ---
    @self.app.callback(
        Output("model-status", "children"),
        [Input("model-selector", "value")]
    )
    def update_model_status(selected_model):
        """Update model status badge when selection changes."""
        return dbc.Alert(
            f"{selected_model} loaded"
            if selected_model in self.embedding_models
            else f"{selected_model} unavailable",
            color="success" if selected_model in self.embedding_models else "danger",
        )

    # --- Callback: render dimension reduction parameters ---
    @self.app.callback(
        Output("dim-reduction-params", "children"),
        Input("dim-reduction-selector", "value"),
    )
    def update_dim_params(method_id):
        """Render tiered parameter inputs for selected dimension reduction method."""
        if not method_id:
            return []
        method_class = MethodRegistry.get_dim_reduction(method_id)
        schema = method_class.param_schema()
        # Get current params or use defaults
        current = getattr(self, f"{method_id}_params", None)
        if current is None:
            current = method_class.default_params()
            setattr(self, f"{method_id}_params", current.copy())
        return create_tiered_param_section(schema, method_id, current, category="dim_reduction")

    # --- Callback: render clustering parameters ---
    @self.app.callback(
        Output("clustering-params", "children"),
        Input("clustering-selector", "value"),
    )
    def update_clustering_params(method_id):
        """Render tiered parameter inputs for selected clustering method."""
        if not method_id:
            return []
        method_class = MethodRegistry.get_clustering(method_id)
        schema = method_class.param_schema()
        # Get current params or use defaults
        current = getattr(self, f"{method_id}_params", None)
        if current is None:
            current = method_class.default_params()
            setattr(self, f"{method_id}_params", current.copy())
        return create_tiered_param_section(schema, method_id, current, category="clustering")

    # --- Callback: toggle comparison mode ---
    @self.app.callback(
        Output("secondary-dim-reduction-container", "style"),
        Input("comparison-mode-toggle", "value"),
    )
    def toggle_comparison_mode(compare_enabled):
        """Show/hide secondary dimension reduction selector."""
        if compare_enabled:
            return {"display": "block"}
        return {"display": "none"}

    # --- Callback: sync dimension reduction parameter values on input change ---
    @self.app.callback(
        Output("param-sync-status", "children"),
        Input({"type": "dim_reduction-param", "algorithm": dash.ALL, "param": dash.ALL}, "value"),
        State({"type": "dim_reduction-param", "algorithm": dash.ALL, "param": dash.ALL}, "id"),
        prevent_initial_call=True,
    )
    def sync_dim_params(values, ids):
        """Update dimension reduction parameter dicts when user edits input fields."""
        from utils.dash_app_functions import auto_cast
        for v, id_dict in zip(values, ids):
            method_id = id_dict["algorithm"]
            param = id_dict["param"]
            # Initialize params dict if it doesn't exist
            params_attr = f"{method_id}_params"
            if not hasattr(self, params_attr) or getattr(self, params_attr) is None:
                method_class = MethodRegistry.get_dim_reduction(method_id)
                setattr(self, params_attr, method_class.default_params().copy())
            # Update the parameter
            getattr(self, params_attr)[param] = auto_cast(v)
        return dbc.Alert("Parameters updated", color="info", duration=2000)

    # --- Callback: sync clustering parameter values on input change ---
    @self.app.callback(
        Output("param-sync-status", "children", allow_duplicate=True),
        Input({"type": "clustering-param", "algorithm": dash.ALL, "param": dash.ALL}, "value"),
        State({"type": "clustering-param", "algorithm": dash.ALL, "param": dash.ALL}, "id"),
        prevent_initial_call=True,
    )
    def sync_cluster_params(values, ids):
        """Update clustering parameter dicts when user edits input fields."""
        from utils.dash_app_functions import auto_cast
        for v, id_dict in zip(values, ids):
            method_id = id_dict["algorithm"]
            param = id_dict["param"]
            # Initialize params dict if it doesn't exist
            params_attr = f"{method_id}_params"
            if not hasattr(self, params_attr) or getattr(self, params_attr) is None:
                method_class = MethodRegistry.get_clustering(method_id)
                setattr(self, params_attr, method_class.default_params().copy())
            # Update the parameter
            getattr(self, params_attr)[param] = auto_cast(v)
        return dbc.Alert("Parameters updated", color="info", duration=2000)

    # --- Callback: toggle dim_reduction tier 2 collapse ---
    @self.app.callback(
        Output({"type": "dim_reduction-tier-collapse", "tier": 2, "algorithm": MATCH}, "is_open"),
        Output({"type": "dim_reduction-tier-toggle", "tier": 2, "algorithm": MATCH}, "children"),
        Input({"type": "dim_reduction-tier-toggle", "tier": 2, "algorithm": MATCH}, "n_clicks"),
        State({"type": "dim_reduction-tier-collapse", "tier": 2, "algorithm": MATCH}, "is_open"),
        prevent_initial_call=True,
    )
    def toggle_dim_tier2(n_clicks, is_open):
        """Toggle dim_reduction Tier 2 collapse and update button text."""
        new_state = not is_open
        button_text = get_toggle_button_text(new_state, tier=2)
        return new_state, button_text

    # --- Callback: toggle dim_reduction tier 3 collapse ---
    @self.app.callback(
        Output({"type": "dim_reduction-tier-collapse", "tier": 3, "algorithm": MATCH}, "is_open"),
        Output({"type": "dim_reduction-tier-toggle", "tier": 3, "algorithm": MATCH}, "children"),
        Input({"type": "dim_reduction-tier-toggle", "tier": 3, "algorithm": MATCH}, "n_clicks"),
        State({"type": "dim_reduction-tier-collapse", "tier": 3, "algorithm": MATCH}, "is_open"),
        prevent_initial_call=True,
    )
    def toggle_dim_tier3(n_clicks, is_open):
        """Toggle dim_reduction Tier 3 collapse and update button text."""
        new_state = not is_open
        button_text = get_toggle_button_text(new_state, tier=3)
        return new_state, button_text

    # --- Callback: toggle clustering tier 2 collapse ---
    @self.app.callback(
        Output({"type": "clustering-tier-collapse", "tier": 2, "algorithm": MATCH}, "is_open"),
        Output({"type": "clustering-tier-toggle", "tier": 2, "algorithm": MATCH}, "children"),
        Input({"type": "clustering-tier-toggle", "tier": 2, "algorithm": MATCH}, "n_clicks"),
        State({"type": "clustering-tier-collapse", "tier": 2, "algorithm": MATCH}, "is_open"),
        prevent_initial_call=True,
    )
    def toggle_cluster_tier2(n_clicks, is_open):
        """Toggle clustering Tier 2 collapse and update button text."""
        new_state = not is_open
        button_text = get_toggle_button_text(new_state, tier=2)
        return new_state, button_text

    # --- Callback: toggle clustering tier 3 collapse ---
    @self.app.callback(
        Output({"type": "clustering-tier-collapse", "tier": 3, "algorithm": MATCH}, "is_open"),
        Output({"type": "clustering-tier-toggle", "tier": 3, "algorithm": MATCH}, "children"),
        Input({"type": "clustering-tier-toggle", "tier": 3, "algorithm": MATCH}, "n_clicks"),
        State({"type": "clustering-tier-collapse", "tier": 3, "algorithm": MATCH}, "is_open"),
        prevent_initial_call=True,
    )
    def toggle_cluster_tier3(n_clicks, is_open):
        """Toggle clustering Tier 3 collapse and update button text."""
        new_state = not is_open
        button_text = get_toggle_button_text(new_state, tier=3)
        return new_state, button_text

    # --- Callback: run analysis with selected methods ---
    @self.app.callback(
        [
            Output("clustering-plot", "figure"),
            Output("current-model-store", "children"),
        ],
        Input("run-analysis-btn", "n_clicks"),
        State("model-selector", "value"),
        State("dim-reduction-selector", "value"),
        State("clustering-selector", "value"),
        State("comparison-mode-toggle", "value"),
        State("dim-reduction-selector-2", "value"),
        prevent_initial_call=True,
    )
    def run_selected_analysis(n_clicks, model, dim_method, cluster_method, compare_mode, dim_method_2):
        """Run analysis with the selected methods."""
        if not n_clicks or not model:
            return dash.no_update, dash.no_update

        print(f"Running analysis: model={model}, dim={dim_method}, cluster={cluster_method}, compare={compare_mode}")

        if model not in self.embedding_models:
            empty_fig = go.Figure()
            empty_fig.add_annotation(
                text=f"Model '{model}' not available.",
                xref="paper", yref="paper", x=0.5, y=0.5,
                showarrow=False, font=dict(size=14, color="red"),
            )
            return empty_fig, model

        # Clear cached results
        cache_key = f"{model}_{dim_method}_{cluster_method}"
        if cache_key in self.analysis_results:
            del self.analysis_results[cache_key]

        if compare_mode and dim_method_2 and dim_method_2 != dim_method:
            # Run comparison mode - both methods
            results1 = self.run_analysis_single(model, dim_method, cluster_method)
            results2 = self.run_analysis_single(model, dim_method_2, cluster_method)
            if results1 and results2:
                fig = self.create_comparison_plot(results1, results2)
                return fig, model
        else:
            # Single method mode
            results = self.run_analysis_single(model, dim_method, cluster_method)
            if results:
                fig = self.create_single_plot(results)
                return fig, model

        # Fallback empty plot
        empty_fig = go.Figure()
        empty_fig.add_annotation(
            text="No data available",
            xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False,
        )
        return empty_fig, model

    # --- Callback: export parameters to YAML ---
    @self.app.callback(
        Output("param-sync-status", "children", allow_duplicate=True),
        Input("export-params-btn", "n_clicks"),
        State("dim-reduction-selector", "value"),
        State("clustering-selector", "value"),
        State("model-selector", "value"),
        prevent_initial_call=True,
    )
    def export_params(n_clicks, dim_method, cluster_method, model):
        """Export current parameters to YAML file."""
        if not n_clicks:
            return dash.no_update

        # Get current params
        dim_params = getattr(self, f"{dim_method}_params", {})
        cluster_params = getattr(self, f"{cluster_method}_params", {})

        try:
            filepath = export_params_yaml(
                dim_method=dim_method,
                dim_params=dim_params,
                cluster_method=cluster_method,
                cluster_params=cluster_params,
                model_name=model,
            )
            return dbc.Alert(f"Parameters exported to {filepath}", color="success", duration=4000)
        except Exception as e:
            logger.error(f"Error exporting params: {e}")
            return dbc.Alert(f"Export failed: {str(e)}", color="danger")

    # --- Callback: update selection info ---
    @self.app.callback(
        [
            Output("selection-info", "children"),
            Output("selected-data-store", "children"),
        ],
        [Input("clustering-plot", "selectedData")],
    )
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

    # --- Callback: handle data export ---
    @self.app.callback(
        Output("export-status", "children"),
        [
            Input("export-json-btn", "n_clicks"),
            Input("export-csv-btn", "n_clicks"),
            Input("copy-clipboard-btn", "n_clicks"),
        ],
        [
            State("selected-data-store", "children"),
            State("current-model-store", "children"),
        ],
    )
    def handle_export(json_clicks, csv_clicks, clipboard_clicks, selected_data_json, current_model):
        """Handle data export."""
        ctx = callback_context
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

    def _format_clipboard_data(self, selected_data: List[Dict]) -> str:
        if not selected_data:
            return "No data selected"
        lines = ["Selected CDE Data", "=" * 50, ""]
        for i, item in enumerate(selected_data, 1):
            lines.extend([
                f"CDE {i}:",
                f"  Tiny ID: {item.get('tinyid', 'N/A')}",
                f"  Domain: {item.get('domain', 'N/A')}",
                f"  Cluster: {item.get('cluster', 'N/A')}",
                f"  Name: {item.get('name', 'N/A')}",
                f"  Question: {item.get('question', 'N/A')}",
                f"  Definition: {item.get('definition', 'N/A')}",
                f"  Coordinates: ({item.get('x', 'N/A'):.3f}, {item.get('y', 'N/A'):.3f})",
                "",
            ])
        return "\n".join(lines)
