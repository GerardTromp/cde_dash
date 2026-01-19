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
from clust_app.utils.functions import logger, date_time_string
from clust_app.utils.methods import MethodRegistry
from clust_app.utils.plot_builder import PlotBuilder


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


def run_clustering_only(
    self,
    model_name: str,
    dim_reduction_method: str,
    clustering_method: str,
    vis_embeddings: NDArray[np.float64],
) -> Optional[Dict[str, Any]]:
    """Run clustering on pre-computed embeddings.

    This is used for clustering comparison mode where we want to apply
    different clustering methods to the same dimension-reduced embeddings.

    Args:
        model_name: Name of the embedding model (for metadata)
        dim_reduction_method: Dimension reduction method ID (for metadata)
        clustering_method: Clustering method ID to apply
        vis_embeddings: Pre-computed visualization embeddings

    Returns:
        Dictionary with analysis results or None if failed
    """
    print(f"\nRunning clustering only: cluster={clustering_method}")
    logger.info(f"Running clustering only: cluster={clustering_method}")

    try:
        # Get method classes from registry
        dim_class = MethodRegistry.get_dim_reduction(dim_reduction_method)
        cluster_class = MethodRegistry.get_clustering(clustering_method)

        # Get clustering parameters
        cluster_params = getattr(self, f"{clustering_method}_params", None)
        if cluster_params is None:
            cluster_params = cluster_class.default_params()

        # Apply clustering on the provided embeddings
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
            "original_embeddings": self.embedding_models.get(model_name),
            "visualization_embeddings": vis_embeddings,
            "cluster_labels": cluster_labels,
            "clusterer": clusterer,
            "metrics": metrics,
        }

    except Exception as e:
        print(f"Clustering failed: {e}")
        logger.error(f"Clustering failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def create_single_plot(self, results: Dict[str, Any]) -> go.Figure:
    """Create a single plot from analysis results.

    Delegates to PlotBuilder for modular, composable plot generation.

    Args:
        results: Dictionary from run_analysis_single()

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

    builder = PlotBuilder(
        results["filtered_cdes"],
        self.d3_colors,
        self._truncate_text,
    )
    return builder.build_single_plot(results)


def create_comparison_plot(
    self, results1: Dict[str, Any], results2: Dict[str, Any]
) -> go.Figure:
    """Create a side-by-side comparison plot of two dimension reduction methods.

    Delegates to PlotBuilder for modular, composable plot generation.

    Args:
        results1: Results from first dimension reduction method
        results2: Results from second dimension reduction method

    Returns:
        Plotly Figure with two subplots
    """
    if not results1 or not results2:
        fig = go.Figure()
        fig.add_annotation(
            text="Comparison data unavailable",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    builder = PlotBuilder(
        results1["filtered_cdes"],
        self.d3_colors,
        self._truncate_text,
    )
    return builder.build_dim_comparison(results1, results2)


def create_clustering_comparison_plot(
    self, results1: Dict[str, Any], results2: Dict[str, Any]
) -> go.Figure:
    """Create a two-row comparison plot of two clustering methods.

    Both results use the same dimension reduction, so embeddings are identical.
    Delegates to PlotBuilder for modular, composable plot generation.

    Args:
        results1: Results from first clustering method
        results2: Results from second clustering method

    Returns:
        Plotly Figure with two row subplots (2 rows x 1 col)
    """
    if not results1 or not results2:
        fig = go.Figure()
        fig.add_annotation(
            text="Comparison data unavailable",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    builder = PlotBuilder(
        results1["filtered_cdes"],
        self.d3_colors,
        self._truncate_text,
    )
    return builder.build_cluster_comparison(results1, results2)


def create_full_comparison_plot(
    self, results_grid: List[List[Dict[str, Any]]]
) -> go.Figure:
    """Create a 2x2 grid comparing dim reduction AND clustering methods.

    Delegates to PlotBuilder for modular, composable plot generation.

    Args:
        results_grid: 2x2 nested list of results:
            [[dim1_clust1, dim1_clust2],
             [dim2_clust1, dim2_clust2]]

    Returns:
        Plotly Figure with 2x2 subplot grid
    """
    if not results_grid or len(results_grid) < 2:
        fig = go.Figure()
        fig.add_annotation(
            text="Invalid comparison grid",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    # Use first valid result for DataFrame reference
    first_result = results_grid[0][0]
    if not first_result:
        fig = go.Figure()
        fig.add_annotation(
            text="Comparison data unavailable",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

    builder = PlotBuilder(
        first_result["filtered_cdes"],
        self.d3_colors,
        self._truncate_text,
    )
    return builder.build_full_comparison(results_grid)
