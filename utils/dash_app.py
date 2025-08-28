import dash  # type: ignore
import dash_bootstrap_components as dbc  # type: ignore
import json
import pandas as pd  # type: ignore
import numpy as np
import pyperclip  # type: ignore
import plotly.graph_objects as go  # type: ignore
from dash import dcc, html, Input, Output, State, callback_context  # type: ignore
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
from utils.functions import logger

# from utils.internal_functions import _get_color_and_shape
from utils.dash_app_functions import (
    update_plot,
    update_selection_info,
    handle_export,
    param_inputs,
    auto_cast,
)


def create_dash_app(self) -> dash.Dash:
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    models = self.embedding_models.keys()
    model_options = []
    for model in models:
        print(model)
        model_options.append({"label": model, "value": model})
    value_option = model_options[0]["value"]
    app.layout = dbc.Container(
        [
            # fmt: off
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1( "Interactive CDE Clustering Analysis (2)", className="text-center mb-4",),
                            html.Hr(),
                        ]
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Tabs(
                                id="models-parameters-tabs",
                                active_tab="model-param-models",
                                children = [
                                    dbc.Tab(
                                        label="ModelsTab", 
                                        tab_id="model-param-models",
                                        children=[
                                            dbc.Card(
                                                [
                                                    dbc.CardHeader("Model Selection"),
                                                    dbc.CardBody(
                                                        [
                                                            dbc.RadioItems( id="model-selector", options=model_options, value=value_option, inline=True,),
                                                            html.Div( id="model-status", className="mt-2"),
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                    dbc.Tab(
                                        label="ParametersTab", 
                                        tab_id="model-param-parameters",
                                        children=[
                                            html.H2("Parameter Configuration"),
                                            dcc.Dropdown(
                                                id="algo-selector",
                                                options=[{"label": k, "value": k} for k in self.params.keys()],
                                                value=["UMAP"],
                                                multi=True,
                                            ),
                                            html.Div(id="param-ui"),
                                            html.Hr(),
                                            dbc.Button("Show Current Params", id="show-params-btn", className="mb-3"),
                                            html.Pre(id="debug-output"),
                                            dbc.Button("Run", id="run-newparams-btn", className="mb-4"),
                                            html.Pre(id="run-state"),
                                        ]
                                    ),
                                ],
                            )
                        ]
                    )
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader(
                                        "Interactive Clustering Visualization"
                                    ),
                                    dbc.CardBody(
                                        [
                                            dcc.Graph(
                                                id="clustering-plot",
                                                style={"height": "700px"},
                                                config={ "displayModeBar": True, "modeBarButtonsToAdd": [ "select2d", "lasso2d", "resetScale2d", ],
                                                    "displaylogo": False,
                                                },
                                            )
                                        ]
                                    ),
                                ]
                            )
                        ]
                    )
                ],
                className="mb-4",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Data Export"),
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.P( "Select data points using lasso or box selection tools above, then export:"),
                                                            html.Div( id="selection-info", className="mb-3",),
                                                        ]
                                                    )
                                                ]
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            dbc.Button( "Export to JSON", id="export-json-btn", color="primary", className="me-2",),
                                                            dbc.Button( "Export to CSV", id="export-csv-btn", color="success", className="me-2",),
                                                            dbc.Button( "Copy to Clipboard", id="copy-clipboard-btn", color="info",),
                                                        ]
                                                    )
                                                ]
                                            ),
                                            dbc.Row(
                                                [
                                                    dbc.Col(
                                                        [
                                                            html.Div( id="export-status", className="mt-3",
                                                            )
                                                        ]
                                                    )
                                                ]
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ]
                    )
                ]
            ),
            # fmt: on
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

    @self.app.callback(
        [
            Output("clustering-plot", "figure"),
            Output("current-model-store", "children"),
        ],
        [Input("model-selector", "value")],
    )
    def _update_plot(selected_model):
        print(selected_model)
        return update_plot(self=self, selected_model=selected_model)

    @self.app.callback(
        [
            Output("selection-info", "children"),
            Output("selected-data-store", "children"),
        ],
        [Input("clustering-plot", "selectedData")],
    )
    def _update_selection_info(selected_data):
        return update_selection_info(selected_data)

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
    def _handle_export(
        json_clicks, csv_clicks, clipboard_clicks, selected_data_json, current_model
    ):
        """Handle data export."""
        ctx = callback_context
        return handle_export(
            self,
            ctx,
            json_clicks,
            csv_clicks,
            clipboard_clicks,
            selected_data_json,
            current_model,
        )

    def _format_clipboard_data(self, selected_data: List[Dict]) -> str:
        if not selected_data:
            return "No data selected"
        lines = ["Selected CDE Data", "=" * 50, ""]
        for i, item in enumerate(selected_data, 1):
            lines.extend(
                [
                    f"CDE {i}:",
                    f"  Tiny ID: {item.get('tiny_id', 'N/A')}",
                    f"  Domain: {item.get('domain', 'N/A')}",
                    f"  Cluster: {item.get('cluster', 'N/A')}",
                    f"  Name: {item.get('name', 'N/A')}",
                    f"  Question: {item.get('question', 'N/A')}",
                    f"  Definition: {item.get('definition', 'N/A')}",
                    f"  Coordinates: ({item.get('x', 'N/A'):.3f}, {item.get('y', 'N/A'):.3f})",
                    "",
                ]
            )
        return "\n".join(lines)

    @self.app.callback(
        Output("model-status", "children"), [Input("model-selector", "value")]
    )
    def update_model_status(selected_model):
        return dbc.Alert(
            (
                f" {selected_model} loaded"
                if selected_model in self.embedding_models
                else f" {selected_model} unavailable"
            ),
            color=("success" if selected_model in self.embedding_models else "danger"),
        )

    # --- Callback: render parameter UIs ---
    @self.app.callback(Output("param-ui", "children"), Input("algo-selector", "value"))
    def update_params(algos):
        if not algos:
            return []
        return [param_inputs(self.params[a], a) for a in algos]

    # --- Callback: update param_sets on any input change ---
    @self.app.callback(
        # self,
        Output("debug-output", "children"),
        Input({"type": "param-input", "algo": dash.ALL, "param": dash.ALL}, "value"),
        State({"type": "param-input", "algo": dash.ALL, "param": dash.ALL}, "id"),
        prevent_initial_call=True,
    )
    def sync_params(values, ids):
        for v, id_dict in zip(values, ids):
            algo = id_dict["algo"]
            param = id_dict["param"]
            self.params[algo][param] = auto_cast(v)  # <-- cast before saving
        # param_string=f"{{\n"
        # for k, v in parameter_sets:
        #     param_string = param_string + print(f"  {k}: {v}\n")
        # param_string = param_string + f"}}"
        return f"Updated Params:\n{self.params}"


# def _format_clipboard_data(self, selected_data: List[Dict]) -> str:
#     if not selected_data:
#         return "No data selected"
#     lines = ["Selected CDE Data", "=" * 50, ""]
#     for i, item in enumerate(selected_data, 1):
#         lines.extend(
#             [
#                 f"CDE {i}:",
#                 f"  Tiny ID: {item.get('tiny_id', 'N/A')}",
#                 f"  Domain: {item.get('domain', 'N/A')}",
#                 f"  Cluster: {item.get('cluster', 'N/A')}",
#                 f"  Name: {item.get('name', 'N/A')}",
#                 f"  Question: {item.get('question', 'N/A')}",
#                 f"  Definition: {item.get('definition', 'N/A')}",
#                 f"  Coordinates: ({item.get('x', 'N/A'):.3f}, {item.get('y', 'N/A'):.3f})",
#                 "",
#             ]
#         )
#     return "\n".join(lines)
