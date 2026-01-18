"""Modular plot builder for composable visualization layouts.

Provides a row-based architecture for building scatter plots that can be
assembled into various layouts: 1x1, 1x2, 2x1, or 2x2 grids.
"""

from typing import Dict, List, Any, Optional, Callable, Tuple
import numpy as np
from numpy.typing import NDArray
import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore


class PlotBuilder:
    """Composable plot builder using row-based architecture.

    This class centralizes all shared plotting logic:
    - Domain-to-color mapping
    - Hover text construction
    - Customdata building for export/selection
    - Trace creation for scatter plots

    Usage:
        builder = PlotBuilder(df, d3_colors, truncate_func)
        fig = builder.build_single_plot(results)
        # or
        fig = builder.build_dim_comparison(results1, results2)
    """

    ROW_HEIGHT = 700  # pixels per row

    def __init__(
        self,
        df,
        d3_colors: List[str],
        truncate_func: Callable[[str, int], str],
    ):
        """Initialize PlotBuilder.

        Args:
            df: DataFrame with filtered CDEs (must have 'domain' column)
            d3_colors: List of color strings for domain coloring
            truncate_func: Function to truncate text (text, max_chars) -> str
        """
        self.df = df
        self.colors = d3_colors
        self._truncate = truncate_func
        self._domain_colors = self._assign_domain_colors()

    def _assign_domain_colors(self) -> Dict[str, str]:
        """Map each domain to a consistent color."""
        domains = self.df["domain"].unique()
        return {
            domain: self.colors[i % len(self.colors)]
            for i, domain in enumerate(domains)
        }

    def _build_hover_text(
        self,
        idx: int,
        cluster_label: int,
        cluster_name: Optional[str] = None,
    ) -> str:
        """Build standardized hover text for a point.

        Args:
            idx: Index into self.df
            cluster_label: Cluster assignment for this point
            cluster_name: Optional clustering method name for label prefix

        Returns:
            HTML-formatted hover text string
        """
        row = self.df.iloc[idx]
        domain = row["domain"]
        name = row.get("name", "N/A")
        question = self._truncate(row.get("question", ""), 50)
        definition = self._truncate(row.get("definition", ""), 50)

        cluster_prefix = f"{cluster_name} " if cluster_name else ""
        return (
            f"<b>{name}</b><br>"
            f"Domain: {domain}<br>"
            f"{cluster_prefix}Cluster: {cluster_label}<br>"
            f"Question: {question}<br>"
            f"Definition: {definition}"
        )

    def _build_customdata(self, idx: int, cluster_label: int) -> List:
        """Build customdata for export/selection.

        Args:
            idx: Index into self.df
            cluster_label: Cluster assignment for this point

        Returns:
            List of [tinyId, cluster, name, question, definition]
        """
        row = self.df.iloc[idx]
        return [
            row.get("tinyId", "N/A"),
            int(cluster_label),
            row.get("name", "N/A"),
            row.get("question", "N/A"),
            row.get("definition", "N/A"),
        ]

    def create_row_traces(
        self,
        embeddings: NDArray[np.float64],
        cluster_labels: NDArray[np.int64],
        cluster_name: Optional[str] = None,
        show_legend: bool = True,
        marker_size: int = 7,
    ) -> List[go.Scatter]:
        """Create scatter traces for one plot row/cell.

        Args:
            embeddings: 2D array (n_samples, 2) of visualization coordinates
            cluster_labels: Array of cluster assignments
            cluster_name: Optional clustering method name for hover text
            show_legend: Whether to show legend entries for these traces
            marker_size: Size of scatter markers

        Returns:
            List of go.Scatter traces, one per domain
        """
        traces = []
        domains = self.df["domain"].unique()

        for domain in domains:
            mask = self.df["domain"] == domain
            indices = np.where(mask)[0]
            color = self._domain_colors[domain]

            hover_text = [
                self._build_hover_text(idx, cluster_labels[idx], cluster_name)
                for idx in indices
            ]
            customdata = [
                self._build_customdata(idx, cluster_labels[idx])
                for idx in indices
            ]

            traces.append(
                go.Scatter(
                    x=embeddings[mask, 0],
                    y=embeddings[mask, 1],
                    mode="markers",
                    name=domain,
                    legendgroup=domain,
                    showlegend=show_legend,
                    marker=dict(color=color, size=marker_size, opacity=0.7),
                    text=hover_text,
                    hoverinfo="text",
                    customdata=customdata,
                )
            )

        return traces

    def _common_layout_settings(self) -> Dict[str, Any]:
        """Return common layout settings for all plot types."""
        return {
            "showlegend": True,
            "legend": dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=1.02,
                title="Domains",
            ),
            "hovermode": "closest",
        }

    def build_single_plot(self, results: Dict[str, Any]) -> go.Figure:
        """Build a single plot (1x1).

        Args:
            results: Dictionary from run_analysis_single() containing:
                - visualization_embeddings
                - cluster_labels
                - dim_reduction_name
                - clustering_name
                - metrics
                - model_name (optional)

        Returns:
            Plotly Figure object
        """
        if not results:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        vis_embeddings = results["visualization_embeddings"]
        cluster_labels = results["cluster_labels"]
        dim_name = results["dim_reduction_name"]
        cluster_name = results["clustering_name"]
        metrics = results["metrics"]
        model_name = results.get("model_name", "Dataset")

        fig = go.Figure()

        traces = self.create_row_traces(
            vis_embeddings, cluster_labels,
            cluster_name=None,  # Don't prefix in hover for single plot
            show_legend=True,
            marker_size=8,
        )
        for trace in traces:
            fig.add_trace(trace)

        # Build title with dataset name as header
        title_text = (
            f"<b>{model_name}</b><br>"
            f"<span style='font-size:14px'>{dim_name} + {cluster_name} | "
            f"Clusters: {metrics['n_clusters']} | "
            f"Silhouette: {metrics['silhouette_score']:.3f}</span>"
        )

        layout = self._common_layout_settings()
        layout.update({
            "title": dict(text=title_text, x=0.5, xanchor="center"),
            "xaxis_title": f"{dim_name} Dimension 1",
            "yaxis_title": f"{dim_name} Dimension 2",
            "height": self.ROW_HEIGHT,
        })
        fig.update_layout(**layout)

        return fig

    def build_dim_comparison(
        self,
        results1: Dict[str, Any],
        results2: Dict[str, Any],
    ) -> go.Figure:
        """Build horizontal comparison (1x2) for different dim reduction methods.

        Args:
            results1: Results from first dimension reduction method
            results2: Results from second dimension reduction method

        Returns:
            Plotly Figure with two side-by-side subplots
        """
        if not results1 or not results2:
            fig = go.Figure()
            fig.add_annotation(
                text="Comparison data unavailable",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        vis1 = results1["visualization_embeddings"]
        vis2 = results2["visualization_embeddings"]
        labels1 = results1["cluster_labels"]
        labels2 = results2["cluster_labels"]
        name1 = results1["dim_reduction_name"]
        name2 = results2["dim_reduction_name"]
        cluster_name = results1["clustering_name"]
        metrics1 = results1["metrics"]
        metrics2 = results2["metrics"]
        model_name = results1.get("model_name", "Dataset")

        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=[
                f"{name1} | Clusters: {metrics1['n_clusters']} | "
                f"Silhouette: {metrics1['silhouette_score']:.3f}",
                f"{name2} | Clusters: {metrics2['n_clusters']} | "
                f"Silhouette: {metrics2['silhouette_score']:.3f}",
            ],
            horizontal_spacing=0.08,
        )

        # Left subplot (method 1)
        traces1 = self.create_row_traces(
            vis1, labels1, cluster_name=None, show_legend=True
        )
        for trace in traces1:
            fig.add_trace(trace, row=1, col=1)

        # Right subplot (method 2)
        traces2 = self.create_row_traces(
            vis2, labels2, cluster_name=None, show_legend=False
        )
        for trace in traces2:
            fig.add_trace(trace, row=1, col=2)

        # Build title with dataset name as header
        title_text = (
            f"<b>{model_name}</b><br>"
            f"<span style='font-size:14px'>Comparison: {name1} vs {name2} "
            f"({cluster_name} clustering)</span>"
        )

        layout = self._common_layout_settings()
        layout.update({
            "title": dict(text=title_text, x=0.5, xanchor="center"),
            "height": self.ROW_HEIGHT,
        })
        fig.update_layout(**layout)

        fig.update_xaxes(title_text=f"{name1} Dim 1", row=1, col=1)
        fig.update_yaxes(title_text=f"{name1} Dim 2", row=1, col=1)
        fig.update_xaxes(title_text=f"{name2} Dim 1", row=1, col=2)
        fig.update_yaxes(title_text=f"{name2} Dim 2", row=1, col=2)

        return fig

    def build_cluster_comparison(
        self,
        results1: Dict[str, Any],
        results2: Dict[str, Any],
    ) -> go.Figure:
        """Build vertical comparison (2x1) for different clustering methods.

        Both results use the same dimension reduction, so embeddings are identical.

        Args:
            results1: Results from first clustering method
            results2: Results from second clustering method

        Returns:
            Plotly Figure with two stacked subplots
        """
        if not results1 or not results2:
            fig = go.Figure()
            fig.add_annotation(
                text="Comparison data unavailable",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        # Both use the same embeddings (same dim reduction method)
        vis_embeddings = results1["visualization_embeddings"]
        labels1 = results1["cluster_labels"]
        labels2 = results2["cluster_labels"]
        dim_name = results1["dim_reduction_name"]
        cluster_name1 = results1["clustering_name"]
        cluster_name2 = results2["clustering_name"]
        metrics1 = results1["metrics"]
        metrics2 = results2["metrics"]
        model_name = results1.get("model_name", "Dataset")

        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=[
                f"<b>{cluster_name1}</b> | Clusters: {metrics1['n_clusters']} | "
                f"Silhouette: {metrics1['silhouette_score']:.3f}",
                f"<b>{cluster_name2}</b> | Clusters: {metrics2['n_clusters']} | "
                f"Silhouette: {metrics2['silhouette_score']:.3f}",
            ],
            vertical_spacing=0.08,
            row_heights=[0.5, 0.5],
        )

        # Row 1: Clustering method 1
        traces1 = self.create_row_traces(
            vis_embeddings, labels1, cluster_name=cluster_name1, show_legend=True
        )
        for trace in traces1:
            fig.add_trace(trace, row=1, col=1)

        # Row 2: Clustering method 2
        traces2 = self.create_row_traces(
            vis_embeddings, labels2, cluster_name=cluster_name2, show_legend=False
        )
        for trace in traces2:
            fig.add_trace(trace, row=2, col=1)

        # Build title with dataset name as header
        title_text = (
            f"<b>{model_name}</b><br>"
            f"<span style='font-size:14px'>Clustering Comparison "
            f"({dim_name} embedding)</span>"
        )

        layout = self._common_layout_settings()
        layout.update({
            "title": dict(text=title_text, x=0.5, xanchor="center"),
            "height": self.ROW_HEIGHT * 2,  # Double height for 2 rows
        })
        fig.update_layout(**layout)

        fig.update_xaxes(title_text=f"{dim_name} Dim 1", row=1, col=1)
        fig.update_yaxes(title_text=f"{dim_name} Dim 2", row=1, col=1)
        fig.update_xaxes(title_text=f"{dim_name} Dim 1", row=2, col=1)
        fig.update_yaxes(title_text=f"{dim_name} Dim 2", row=2, col=1)

        return fig

    def build_full_comparison(
        self,
        results_grid: List[List[Dict[str, Any]]],
    ) -> go.Figure:
        """Build 2x2 grid comparing dim reduction AND clustering methods.

        Args:
            results_grid: 2x2 nested list of results:
                [[dim1_clust1, dim1_clust2],
                 [dim2_clust1, dim2_clust2]]

        Returns:
            Plotly Figure with 2x2 subplot grid
        """
        # Validate grid
        if (
            not results_grid
            or len(results_grid) != 2
            or len(results_grid[0]) != 2
            or len(results_grid[1]) != 2
        ):
            fig = go.Figure()
            fig.add_annotation(
                text="Invalid comparison grid",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig

        # Check for empty results
        for row in results_grid:
            for r in row:
                if not r:
                    fig = go.Figure()
                    fig.add_annotation(
                        text="Comparison data unavailable",
                        xref="paper", yref="paper",
                        x=0.5, y=0.5, showarrow=False
                    )
                    return fig

        # Extract names from results
        dim_name1 = results_grid[0][0]["dim_reduction_name"]
        dim_name2 = results_grid[1][0]["dim_reduction_name"]
        cluster_name1 = results_grid[0][0]["clustering_name"]
        cluster_name2 = results_grid[0][1]["clustering_name"]
        model_name = results_grid[0][0].get("model_name", "Dataset")

        # Build subplot titles
        subplot_titles = []
        for r_idx, row in enumerate(results_grid):
            for c_idx, res in enumerate(row):
                m = res["metrics"]
                dim_n = res["dim_reduction_name"]
                clust_n = res["clustering_name"]
                subplot_titles.append(
                    f"{dim_n} + {clust_n} | C:{m['n_clusters']} | "
                    f"S:{m['silhouette_score']:.2f}"
                )

        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=subplot_titles,
            horizontal_spacing=0.08,
            vertical_spacing=0.10,
        )

        # Add traces for each cell
        for r_idx, row in enumerate(results_grid):
            for c_idx, res in enumerate(row):
                show_legend = (r_idx == 0 and c_idx == 0)
                traces = self.create_row_traces(
                    res["visualization_embeddings"],
                    res["cluster_labels"],
                    cluster_name=res["clustering_name"],
                    show_legend=show_legend,
                )
                for trace in traces:
                    fig.add_trace(trace, row=r_idx + 1, col=c_idx + 1)

        # Build title
        title_text = (
            f"<b>{model_name}</b><br>"
            f"<span style='font-size:14px'>Full Comparison: "
            f"{dim_name1} vs {dim_name2} × {cluster_name1} vs {cluster_name2}</span>"
        )

        layout = self._common_layout_settings()
        layout.update({
            "title": dict(text=title_text, x=0.5, xanchor="center"),
            "height": self.ROW_HEIGHT * 2,  # Double height for 2 rows
        })
        fig.update_layout(**layout)

        # Update axes labels
        for r_idx in range(2):
            for c_idx in range(2):
                res = results_grid[r_idx][c_idx]
                dim_n = res["dim_reduction_name"]
                fig.update_xaxes(
                    title_text=f"{dim_n} Dim 1", row=r_idx + 1, col=c_idx + 1
                )
                fig.update_yaxes(
                    title_text=f"{dim_n} Dim 2", row=r_idx + 1, col=c_idx + 1
                )

        return fig
