import umap  # type: ignore
import numpy as np
import time
import plotly.graph_objects as go  # type: ignore
from plotly.subplots import make_subplots  # type: ignore
from tqdm import tqdm
from numpy.typing import NDArray
from typing import Dict, List, Tuple, Optional, Any, Union
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import HDBSCAN  # type: ignore
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
from utils.functions import logger, date_time_string
from utils.methods import MethodRegistry


def apply_dimensionality_reduction(
    self, embeddings: np.ndarray, method: str = "tsne"
) -> np.ndarray:
    """Apply t-SNE or UMAP for visualization"""
    print(f"Applying {method.upper()}...")
    logger.info(f"Applying {method} reduction")
    start_time = time.time()
    scaler = StandardScaler()
    embeddings_scaled = scaler.fit_transform(embeddings)
    # print(f"{self.analysis_params}\n")
    # tsne_params = self.analysis_params["TSNE"]
    # umap_params = self.analysis_params["UMAP"]
    tsne_params = self.tsne_params
    umap_params = self.umap_params
    # print(f"modified TSNE params {tsne_params}\n")
    # print(f"modified UMAP params {umap_params}\n")
    ####
    # Move the parameter update out of this function so that the dash app can dynamically update the dictionary
    tsne_local = {
        "n_components": 2,
        "random_state": 42,
        "perplexity": min(30, len(embeddings) // 4),
        "metric": "cosine",
        "method": "exact",
    }
    tsne_params.update(tsne_local)
    umap_local = {
        "n_components": 2,
        "random_state": 42,
        "n_neighbors": min(15, len(embeddings) // 3),
        "min_dist": 0.1,
        "metric": "cosine",
    }
    umap_params.update(umap_local)
    if method == "tsne":
        # reducer = TSNE(n_components=2, random_state=42, perplexity=min(30, len(embeddings) // 4), metric='cosine', method='exact')
        reducer = TSNE(**tsne_params)
    elif method == "umap":
        # reducer = umap.UMAP(n_components=2, random_state=42, n_neighbors=min(15, len(embeddings) // 3), min_dist=0.1, metric='cosine')
        reducer = umap.UMAP(**umap_params)
    else:
        raise ValueError(f"Unknown method: {method}")
    reduced_embeddings = reducer.fit_transform(embeddings_scaled)
    print(
        f"Completed {method.upper()} in {time.time() - start_time:.2f} seconds, shape: {reduced_embeddings.shape}"
    )
    logger.info(f"{method} reduction shape: {reduced_embeddings.shape}")
    return reduced_embeddings


def apply_clustering(self, embeddings: np.ndarray) -> Tuple[np.ndarray, HDBSCAN]:
    """HDBSCAN clustering"""
    print("Applying HDBSCAN clustering...")
    logger.info(f"Clustering embeddings shape: {embeddings.shape}")
    start_time = time.time()
    clusterer = HDBSCAN(**self.hdbscan_params)
    cluster_labels = clusterer.fit_predict(embeddings)
    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    n_noise = list(cluster_labels).count(-1)
    print(
        f"Completed clustering: {n_clusters} clusters, {n_noise} noise points in {time.time() - start_time:.2f} seconds"
    )
    logger.info(
        f"Clusters: {n_clusters}, Noise: {n_noise}, Coverage: {(len(cluster_labels) - n_noise) / len(cluster_labels):.4f}"
    )
    return cluster_labels, clusterer


def evaluate_clustering(
    self, embeddings: np.ndarray, cluster_labels: np.ndarray
) -> Dict[str, float]:
    """Evaluate clustering quality"""
    valid_mask = cluster_labels != -1
    n_total = len(cluster_labels)
    n_clustered = np.sum(valid_mask)
    coverage = n_clustered / n_total
    if not np.any(valid_mask) or len(set(cluster_labels[valid_mask])) < 2:
        return {
            "silhouette_score": 0.0,
            "coverage": coverage,
            "n_clusters": 0,
            "n_noise": n_total - n_clustered,
            "avg_cluster_size": 0.0,
        }
    valid_embeddings = embeddings[valid_mask]
    valid_labels = cluster_labels[valid_mask]
    silhouette = silhouette_score(valid_embeddings, valid_labels)
    cluster_sizes = np.bincount(valid_labels)
    return {
        "silhouette_score": silhouette,  # type: ignore
        "coverage": coverage,
        "n_clusters": len(set(valid_labels)),
        "n_noise": n_total - n_clustered,
        "avg_cluster_size": cluster_sizes.mean(),
    }


##################################
# This should be generalized to permit any model to be run
#    Changing to load precomputed embeddings
#    Change design to separate embedding and analysis
#
def run_analysis(self, model_name: str = "all-MiniLM-L6-v2") -> Dict[str, Any]:
    """Run clustering analysis with t-SNE and UMAP"""
    print(f"\nStarting analysis with {model_name}...")
    logger.info(f"Running analysis with {model_name}")
    # try:
    #     import torch

    #     torch.manual_seed(42)
    # except ImportError:
    #     logger.warning("PyTorch unavailable")
    np.random.seed(42)

    if not self.embedding_models:
        self.load_embedding_models()
    if (
        model_name not in self.embedding_models
        or self.filtered_cdes is None
        or len(self.filtered_cdes) == 0
    ):
        print(f"Model {model_name} or data unavailable")
        logger.error(f"Model {model_name} or data unavailable")
        return {}

    texts = self.filtered_cdes["combined_text"].tolist()
    # embeddings = self.compute_embeddings(model_name, texts)
    embeddings = self.embedding_models[model_name]
    visualization_methods = ["tsne", "umap"]
    visualization_embeddings = {}
    clustering_results = {}
    self.all_metrics[model_name] = {}

    for method in visualization_methods:
        try:
            vis_embeddings = self.apply_dimensionality_reduction(embeddings, method)
            cluster_labels, clusterer = self.apply_clustering(vis_embeddings)
            visualization_embeddings[method] = vis_embeddings
            clustering_results[method] = {
                "cluster_labels": cluster_labels,
                "clusterer": clusterer,
            }
            self.all_metrics[model_name][method] = self.evaluate_clustering(
                vis_embeddings, cluster_labels
            )
            print(
                f"Completed {method.upper()} analysis: {self.all_metrics[model_name][method]['n_clusters']} clusters"
            )
        except Exception as e:
            print(f"Failed {method.upper()} analysis: {e}")
            logger.warning(f"Failed {method} analysis: {e}")

    print(f"Analysis complete for {model_name}")
    return {
        "model_name": model_name,
        "filtered_cdes": self.filtered_cdes,
        "original_embeddings": embeddings,
        "visualization_embeddings": visualization_embeddings,
        "clustering_results": clustering_results,
    }


def run_analysis_single(
    self,
    model_name: str,
    dim_reduction_method: str = "umap",
    clustering_method: str = "hdbscan",
) -> Optional[Dict[str, Any]]:
    """Run analysis with single selected methods using the modular registry.

    Args:
        model_name: Name of the embedding model to use
        dim_reduction_method: Dimension reduction method ID (e.g., "umap", "tsne", "pca")
        clustering_method: Clustering method ID (e.g., "hdbscan", "dbscan", "kmeans", "spectral")

    Returns:
        Dictionary with analysis results or None if failed
    """
    print(f"\nRunning analysis: model={model_name}, dim={dim_reduction_method}, cluster={clustering_method}")
    logger.info(f"Running analysis: model={model_name}, dim={dim_reduction_method}, cluster={clustering_method}")

    np.random.seed(42)

    if not self.embedding_models:
        self.load_embedding_models()

    if (
        model_name not in self.embedding_models
        or self.filtered_cdes is None
        or len(self.filtered_cdes) == 0
    ):
        print(f"Model {model_name} or data unavailable")
        logger.error(f"Model {model_name} or data unavailable")
        return None

    embeddings = self.embedding_models[model_name]

    try:
        # Get method classes from registry
        dim_class = MethodRegistry.get_dim_reduction(dim_reduction_method)
        cluster_class = MethodRegistry.get_clustering(clustering_method)

        # Get parameters (use stored params or defaults)
        dim_params = getattr(self, f"{dim_reduction_method}_params", None)
        if dim_params is None:
            dim_params = dim_class.default_params()

        cluster_params = getattr(self, f"{clustering_method}_params", None)
        if cluster_params is None:
            cluster_params = cluster_class.default_params()

        # Apply dimension reduction
        print(f"Applying {dim_class.name} dimension reduction...")
        start_time = time.time()
        dim_reducer = dim_class()
        vis_embeddings = dim_reducer.fit_transform(embeddings, dim_params)
        print(f"Completed {dim_class.name} in {time.time() - start_time:.2f}s, shape: {vis_embeddings.shape}")

        # Apply clustering
        print(f"Applying {cluster_class.name} clustering...")
        start_time = time.time()
        clusterer_instance = cluster_class()
        cluster_labels, clusterer = clusterer_instance.fit_predict(vis_embeddings, cluster_params)
        n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
        n_noise = list(cluster_labels).count(-1)
        print(f"Completed {cluster_class.name}: {n_clusters} clusters, {n_noise} noise points in {time.time() - start_time:.2f}s")

        # Evaluate clustering
        metrics = self.evaluate_clustering(vis_embeddings, cluster_labels)

        return {
            "model_name": model_name,
            "dim_reduction_method": dim_reduction_method,
            "dim_reduction_name": dim_class.name,
            "clustering_method": clustering_method,
            "clustering_name": cluster_class.name,
            "filtered_cdes": self.filtered_cdes,
            "original_embeddings": embeddings,
            "visualization_embeddings": vis_embeddings,
            "cluster_labels": cluster_labels,
            "clusterer": clusterer,
            "metrics": metrics,
        }

    except Exception as e:
        print(f"Analysis failed: {e}")
        logger.error(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_single_plot(self, results: Dict[str, Any]) -> go.Figure:
    """Create a single plot from analysis results.

    Args:
        results: Dictionary from run_analysis_single()

    Returns:
        Plotly Figure object
    """
    if not results:
        fig = go.Figure()
        fig.add_annotation(text="No data available", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    df = results["filtered_cdes"]
    vis_embeddings = results["visualization_embeddings"]
    cluster_labels = results["cluster_labels"]
    dim_name = results["dim_reduction_name"]
    cluster_name = results["clustering_name"]
    metrics = results["metrics"]

    fig = go.Figure()

    # Get unique domains and assign colors
    domains = df["domain"].unique()
    colors = self.d3_colors

    for i, domain in enumerate(domains):
        mask = df["domain"] == domain
        indices = np.where(mask)[0]

        hover_text = [
            f"<b>{df.iloc[idx]['name']}</b><br>"
            f"Domain: {domain}<br>"
            f"Cluster: {cluster_labels[idx]}<br>"
            f"Question: {self._truncate_text(df.iloc[idx].get('question', ''), 50)}<br>"
            f"Definition: {self._truncate_text(df.iloc[idx].get('definition', ''), 50)}"
            for idx in indices
        ]

        customdata = [
            [
                df.iloc[idx].get("tinyId", "N/A"),
                int(cluster_labels[idx]),
                df.iloc[idx].get("name", "N/A"),
                df.iloc[idx].get("question", "N/A"),
                df.iloc[idx].get("definition", "N/A"),
            ]
            for idx in indices
        ]

        fig.add_trace(
            go.Scatter(
                x=vis_embeddings[mask, 0],
                y=vis_embeddings[mask, 1],
                mode="markers",
                name=domain,
                legendgroup=domain,
                marker=dict(
                    color=colors[i % len(colors)],
                    size=8,
                    opacity=0.7,
                ),
                text=hover_text,
                hoverinfo="text",
                customdata=customdata,
            )
        )

    fig.update_layout(
        title=f"{dim_name} + {cluster_name} | Clusters: {metrics['n_clusters']} | Silhouette: {metrics['silhouette_score']:.3f}",
        xaxis_title=f"{dim_name} Dimension 1",
        yaxis_title=f"{dim_name} Dimension 2",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            title="Domains",
        ),
        height=700,
        hovermode="closest",
    )

    return fig


def create_comparison_plot(self, results1: Dict[str, Any], results2: Dict[str, Any]) -> go.Figure:
    """Create a side-by-side comparison plot of two dimension reduction methods.

    Args:
        results1: Results from first dimension reduction method
        results2: Results from second dimension reduction method

    Returns:
        Plotly Figure with two subplots
    """
    if not results1 or not results2:
        fig = go.Figure()
        fig.add_annotation(text="Comparison data unavailable", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    df = results1["filtered_cdes"]
    vis1 = results1["visualization_embeddings"]
    vis2 = results2["visualization_embeddings"]
    labels1 = results1["cluster_labels"]
    labels2 = results2["cluster_labels"]
    name1 = results1["dim_reduction_name"]
    name2 = results2["dim_reduction_name"]
    cluster_name = results1["clustering_name"]
    metrics1 = results1["metrics"]
    metrics2 = results2["metrics"]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            f"{name1} | Clusters: {metrics1['n_clusters']} | Silhouette: {metrics1['silhouette_score']:.3f}",
            f"{name2} | Clusters: {metrics2['n_clusters']} | Silhouette: {metrics2['silhouette_score']:.3f}",
        ],
        horizontal_spacing=0.08,
    )

    domains = df["domain"].unique()
    colors = self.d3_colors

    for i, domain in enumerate(domains):
        mask = df["domain"] == domain
        indices = np.where(mask)[0]
        color = colors[i % len(colors)]

        # Helper to build hover text
        def build_hover(idx, labels):
            return (
                f"<b>{df.iloc[idx]['name']}</b><br>"
                f"Domain: {domain}<br>"
                f"Cluster: {labels[idx]}<br>"
                f"Question: {self._truncate_text(df.iloc[idx].get('question', ''), 50)}<br>"
                f"Definition: {self._truncate_text(df.iloc[idx].get('definition', ''), 50)}"
            )

        def build_customdata(idx, labels):
            return [
                df.iloc[idx].get("tinyId", "N/A"),
                int(labels[idx]),
                df.iloc[idx].get("name", "N/A"),
                df.iloc[idx].get("question", "N/A"),
                df.iloc[idx].get("definition", "N/A"),
            ]

        # Left subplot (method 1)
        fig.add_trace(
            go.Scatter(
                x=vis1[mask, 0],
                y=vis1[mask, 1],
                mode="markers",
                name=domain,
                legendgroup=domain,
                showlegend=True,
                marker=dict(color=color, size=7, opacity=0.7),
                text=[build_hover(idx, labels1) for idx in indices],
                hoverinfo="text",
                customdata=[build_customdata(idx, labels1) for idx in indices],
            ),
            row=1, col=1,
        )

        # Right subplot (method 2)
        fig.add_trace(
            go.Scatter(
                x=vis2[mask, 0],
                y=vis2[mask, 1],
                mode="markers",
                name=domain,
                legendgroup=domain,
                showlegend=False,
                marker=dict(color=color, size=7, opacity=0.7),
                text=[build_hover(idx, labels2) for idx in indices],
                hoverinfo="text",
                customdata=[build_customdata(idx, labels2) for idx in indices],
            ),
            row=1, col=2,
        )

    fig.update_layout(
        title=f"Comparison: {name1} vs {name2} ({cluster_name} clustering)",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            title="Domains",
        ),
        height=700,
        hovermode="closest",
    )

    fig.update_xaxes(title_text=f"{name1} Dim 1", row=1, col=1)
    fig.update_yaxes(title_text=f"{name1} Dim 2", row=1, col=1)
    fig.update_xaxes(title_text=f"{name2} Dim 1", row=1, col=2)
    fig.update_yaxes(title_text=f"{name2} Dim 2", row=1, col=2)

    return fig


def create_clustering_comparison_plot(self, results1: Dict[str, Any], results2: Dict[str, Any]) -> go.Figure:
    """Create a side-by-side comparison plot of two clustering methods.

    Both results use the same dimension reduction, so embeddings are identical.
    The subplots show how different clustering algorithms partition the same embedding space.

    Args:
        results1: Results from first clustering method
        results2: Results from second clustering method

    Returns:
        Plotly Figure with two subplots
    """
    if not results1 or not results2:
        fig = go.Figure()
        fig.add_annotation(text="Comparison data unavailable", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    df = results1["filtered_cdes"]
    # Both use the same embeddings (same dim reduction method)
    vis_embeddings = results1["visualization_embeddings"]
    labels1 = results1["cluster_labels"]
    labels2 = results2["cluster_labels"]
    dim_name = results1["dim_reduction_name"]
    cluster_name1 = results1["clustering_name"]
    cluster_name2 = results2["clustering_name"]
    metrics1 = results1["metrics"]
    metrics2 = results2["metrics"]

    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=[
            f"{cluster_name1} | Clusters: {metrics1['n_clusters']} | Silhouette: {metrics1['silhouette_score']:.3f}",
            f"{cluster_name2} | Clusters: {metrics2['n_clusters']} | Silhouette: {metrics2['silhouette_score']:.3f}",
        ],
        horizontal_spacing=0.08,
    )

    domains = df["domain"].unique()
    colors = self.d3_colors

    for i, domain in enumerate(domains):
        mask = df["domain"] == domain
        indices = np.where(mask)[0]
        color = colors[i % len(colors)]

        # Helper to build hover text
        def build_hover(idx, labels, cluster_name):
            return (
                f"<b>{df.iloc[idx]['name']}</b><br>"
                f"Domain: {domain}<br>"
                f"{cluster_name} Cluster: {labels[idx]}<br>"
                f"Question: {self._truncate_text(df.iloc[idx].get('question', ''), 50)}<br>"
                f"Definition: {self._truncate_text(df.iloc[idx].get('definition', ''), 50)}"
            )

        def build_customdata(idx, labels):
            return [
                df.iloc[idx].get("tinyId", "N/A"),
                int(labels[idx]),
                df.iloc[idx].get("name", "N/A"),
                df.iloc[idx].get("question", "N/A"),
                df.iloc[idx].get("definition", "N/A"),
            ]

        # Left subplot (clustering method 1)
        fig.add_trace(
            go.Scatter(
                x=vis_embeddings[mask, 0],
                y=vis_embeddings[mask, 1],
                mode="markers",
                name=domain,
                legendgroup=domain,
                showlegend=True,
                marker=dict(color=color, size=7, opacity=0.7),
                text=[build_hover(idx, labels1, cluster_name1) for idx in indices],
                hoverinfo="text",
                customdata=[build_customdata(idx, labels1) for idx in indices],
            ),
            row=1, col=1,
        )

        # Right subplot (clustering method 2)
        fig.add_trace(
            go.Scatter(
                x=vis_embeddings[mask, 0],
                y=vis_embeddings[mask, 1],
                mode="markers",
                name=domain,
                legendgroup=domain,
                showlegend=False,
                marker=dict(color=color, size=7, opacity=0.7),
                text=[build_hover(idx, labels2, cluster_name2) for idx in indices],
                hoverinfo="text",
                customdata=[build_customdata(idx, labels2) for idx in indices],
            ),
            row=1, col=2,
        )

    fig.update_layout(
        title=f"Clustering Comparison: {cluster_name1} vs {cluster_name2} ({dim_name} embedding)",
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=1.02,
            title="Domains",
        ),
        height=700,
        hovermode="closest",
    )

    fig.update_xaxes(title_text=f"{dim_name} Dim 1", row=1, col=1)
    fig.update_yaxes(title_text=f"{dim_name} Dim 2", row=1, col=1)
    fig.update_xaxes(title_text=f"{dim_name} Dim 1", row=1, col=2)
    fig.update_yaxes(title_text=f"{dim_name} Dim 2", row=1, col=2)

    return fig
