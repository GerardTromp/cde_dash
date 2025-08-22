#!/usr/bin/env python3
"""
Interactive CDE clustering analysis with Dash and Plotly.
Data point selection with lasso/box & export tooltip data to JSON/CSV or clipboard
This version comes with faceted t-SNE/UMAP plots for SAPBERT/MedCPT
"""

# import logging
import warnings

# import time
import matplotlib.pyplot as plt  # type: ignore
import seaborn as sns  # type: ignore
from sklearn.preprocessing import StandardScaler
from sklearn.manifold import TSNE
# from sentence_transformers import SentenceTransformer  # type: ignore
from pathlib import Path
from collections import defaultdict
from utils.functions import (
    logger,
    extract_text_fields,
    create_faceted_plots,
    load_domain_mapping,
    load_cde_data,
    load_embedding_models,
    load_configs,
)
from utils.dash_app import create_dash_app, setup_callbacks
from utils.argparse import cde_argparse
from utils.internal_functions import (
    _truncate_text,
    _get_color_and_shape,
    _create_faceted_comparison_figure,
    _clean_text,
)
from utils.run_analysis import run_analysis, apply_clustering, apply_dimensionality_reduction, evaluate_clustering

warnings.filterwarnings("ignore")

# Dash imports


class InteractiveClusteringAnalyzer:
    """Interactive CDE clustering analyzer with Dash interface."""

    def __init__(
        self, hdbscan_min_cluster_size: int = 15, hdbscan_min_samples: int = 5
    ):
        """Initialize analyzer with HDBSCAN parameters."""
        self.hdbscan_params = {
            "min_cluster_size": hdbscan_min_cluster_size,
            "min_samples": hdbscan_min_samples,
            "metric": "euclidean",
        }
        # self._setup_gpu_config()
        self.d3_colors = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
            "#aec7e8",
            "#ffbb78",
            "#98df8a",
            "#ff9896",
            "#c5b0d5",
            "#c49c94",
            "#f7b6d3",
            "#c7c7c7",
            "#dbdb8d",
            "#9edae5",
        ]
        self.marker_shapes = [
            "circle",
            "square",
            "diamond",
            "cross",
            "x",
            "triangle-up",
            "triangle-down",
            "star",
        ]
        self.embedding_models = {}
        self.tokenizers = {}
        self.domain_mapping = None
        self.cde_data = None
        self.filtered_cdes = None
        self.all_metrics = {}
        self.analysis_results = {}
        self.config = {}
        self.hdbscan_params = {}
        self.umap_params = {}
        self.tsne_params = {}
        self.app = None
        logger.info(
            f"Initialized with HDBSCAN: min_cluster_size={hdbscan_min_cluster_size}, min_samples={hdbscan_min_samples}"
        )

    load_domain_mapping = load_domain_mapping
    extract_text_fields = extract_text_fields
    evaluate_clustering = evaluate_clustering
    load_cde_data = load_cde_data
    create_dash_app = create_dash_app
    setup_callbacks = setup_callbacks
    load_embedding_models = load_embedding_models
    load_configs = load_configs
    _truncate_text = _truncate_text
    _get_color_and_shape = _get_color_and_shape
    _create_faceted_comparison_figure = _create_faceted_comparison_figure 
    _clean_text = _clean_text 
    run_analysis = run_analysis
    apply_clustering = apply_clustering
    apply_dimensionality_reduction = apply_dimensionality_reduction
    create_faceted_plots =  create_faceted_plots


def main():
    args = cde_argparse()

    analyzer = InteractiveClusteringAnalyzer(
        # hdbscan_min_cluster_size=15, hdbscan_min_samples=5
    )
    config = load_configs(path=args.config_path)
    if len(config) == 0:
        print("Error: could not load configs")
        return
    else:
        analyzer.config = config
    params = load_configs(path=args.param_path)
    if len(params) == 0:
        print("Error: could not load params")
        return
    else:
        analyzer.umap_params = params["UMAP"]
        analyzer.tsne_params = params["TSNE"]
        analyzer.hdbscan_params = params["HDBSCAN"]

    domain_df = analyzer.load_domain_mapping()
    if domain_df.empty:
        print("Error: No domain mapping loaded")
        return
    cde_df = analyzer.load_cde_data()
    if cde_df.empty:
        print("Error: No CDE data loaded")
        return
    processed_df = analyzer.extract_text_fields(cde_df)
    if processed_df.empty:
        print("Error: No processed CDE data")
        return
    analyzer.filtered_cdes = processed_df  # type: ignore
    try:
        analyzer.load_embedding_models()
        print("All embedding models loaded successfully")
    except Exception as e:
        print(f"\n--- Error loading models: {e}---\n")
    print(f"These are the models loaded into 'embeddding_models': {analyzer.embedding_models.keys()}")
    print("Creating Dash application...")
    app = analyzer.create_dash_app()
    print("Setting up interactive callbacks...")
    analyzer.setup_callbacks()
    print("\nInteractive Clustering Analysis Ready")
    # print("Open browser to: http://127.0.0.1:8050")
    try:
        app.run(debug=False, host="127.0.0.1", port=8050)
    except KeyboardInterrupt:
        print("Session ended by user")
    except Exception as e:
        logger.error(f"Dash server error: {e}")
        print(f"Error running Dash server: {e}")


if __name__ == "__main__":
    main()

    # def _setup_gpu_config(self) -> None:
    #     """Configure GPU for PyTorch models."""
    #     try:
    #         import torch

    #         if torch.cuda.is_available():
    #             gpu_count = torch.cuda.device_count()
    #             logger.info(f"Found {gpu_count} GPU(s)")
    #             self.device = torch.device("cuda:0")
    #             self.secondary_device = torch.device(
    #                 "cuda:1" if gpu_count >= 2 else "cuda:0"
    #             )
    #             self.use_multi_gpu = gpu_count >= 2
    #             logger.info(
    #                 f"{'Multi' if self.use_multi_gpu else 'Single'} GPU setup: using {self.device}"
    #             )
    #         else:
    #             self.device = self.secondary_device = torch.device("cpu")
    #             self.use_multi_gpu = False
    #             logger.info("Using CPU")
    #     except ImportError:
    #         self.device = self.secondary_device = None
    #         self.use_multi_gpu = False
    #         logger.warning("PyTorch unavailable, GPU disabled")

    # def load_embedding_models(self) -> None:
    #     print("Loading embedding models...")
    #     logger.info("Loading embedding models")
    #     try:
    #         self.embedding_models["all-MiniLM-L6-v2"] = SentenceTransformer(
    #             "all-MiniLM-L6-v2"
    #         )
    #         print("Loaded all-MiniLM-L6-v2")
    #         logger.info("Loaded all-MiniLM-L6-v2")
    #     except Exception as e:
    #         print(f"Failed to load all-MiniLM-L6-v2: {e}")
    #         logger.error(f"Failed to load all-MiniLM-L6-v2: {e}")

    #     try:
    #         from transformers import AutoTokenizer, AutoModel

    #         self.tokenizers["SAPBERT"] = AutoTokenizer.from_pretrained(
    #             "cambridgeltl/SapBERT-from-PubMedBERT-fulltext"
    #         )
    #         self.embedding_models["SAPBERT"] = AutoModel.from_pretrained(
    #             "cambridgeltl/SapBERT-from-PubMedBERT-fulltext"
    #         )
    #         print("Loaded SAPBERT")
    #         logger.info("Loaded SAPBERT")
    #     except Exception as e:
    #         print(f"Failed to load SAPBERT: {e}")
    #         logger.error(f"Failed to load SAPBERT: {e}")

    #     try:
    #         self.tokenizers["MedCPT"] = AutoTokenizer.from_pretrained(
    #             "ncbi/MedCPT-Query-Encoder"
    #         )
    #         self.embedding_models["MedCPT"] = AutoModel.from_pretrained(
    #             "ncbi/MedCPT-Query-Encoder"
    #         )
    #         print("Loaded MedCPT")
    #         logger.info("Loaded MedCPT")
    #     except Exception as e:
    #         print(f"Failed to load MedCPT: {e}")
    #         logger.error(f"Failed to load MedCPT: {e}")

    # def compute_embeddings_sentence_transformer(
    #     self, model, texts: List[str]
    # ) -> np.ndarray:
    #     print(f"Computing embeddings for {len(texts)} texts with all-MiniLM-L6-v2...")
    #     logger.info(f"Computing embeddings for {len(texts)} texts")
    #     start_time = time.time()
    #     processed_texts = [
    #         re.sub(r"[^\w\s\.\,\;\:\!\?\-\(\)]", " ", str(text).strip() or "empty text")
    #         for text in texts
    #     ]
    #     try:
    #         embeddings = model.encode(processed_texts, show_progress_bar=True)
    #         print(
    #             f"Completed all-MiniLM-L6-v2 embeddings in {time.time() - start_time:.2f} seconds, shape: {embeddings.shape}"
    #         )
    #         logger.info(f"Computed embeddings shape: {embeddings.shape}")
    #         return embeddings
    #     except Exception as e:
    #         print(f"Error computing embeddings: {e}")
    #         logger.error(f"Error computing embeddings: {e}")
    #         return np.zeros((len(texts), 384))

    # def compute_embeddings_transformers(
    #     self, model, tokenizer, texts: List[str]
    # ) -> np.ndarray:
    #     """Compute embeddings - GPU preferred"""
    #     print(f"Computing embeddings for {len(texts)} texts with SAPBERT...")
    #     logger.info(f"Computing transformers embeddings for {len(texts)} texts")
    #     import torch

    #     start_time = time.time()
    #     if self.device and self.device.type == "cuda":
    #         model = model.to(self.device)
    #     processed_texts = [
    #         re.sub(r"[^\w\s\.\,\;\:\!\?\-\(\)]", " ", str(text).strip() or "empty text")
    #         for text in texts
    #     ]
    #     batch_size = 64 if self.device and self.device.type == "cuda" else 32
    #     all_embeddings = []

    #     for i in tqdm(
    #         range(0, len(processed_texts), batch_size),
    #         desc="Processing SAPBERT batches",
    #     ):
    #         batch_texts = processed_texts[i : i + batch_size]
    #         try:
    #             encoded = tokenizer(
    #                 batch_texts,
    #                 truncation=True,
    #                 padding=True,
    #                 return_tensors="pt",
    #                 max_length=512,
    #             )
    #             if self.device and self.device.type == "cuda":
    #                 encoded = {k: v.to(self.device) for k, v in encoded.items()}
    #             with torch.no_grad():
    #                 output = model(**encoded)
    #                 cls_embeddings = output[0][:, 0, :].cpu().numpy()
    #                 all_embeddings.append(cls_embeddings)
    #         except Exception as e:
    #             logger.warning(f"Error in batch {i//batch_size + 1}: {e}")
    #             all_embeddings.append(np.zeros((len(batch_texts), 768)))

    #     embeddings = (
    #         np.concatenate(all_embeddings, axis=0)
    #         if all_embeddings
    #         else np.zeros((len(texts), 768))
    #     )
    #     print(
    #         f"Completed SAPBERT embeddings in {time.time() - start_time:.2f} seconds, shape: {embeddings.shape}"
    #     )
    #     logger.info(f"Computed embeddings shape: {embeddings.shape}")
    #     return embeddings

    # def compute_embeddings_medcpt(
    #     self, model, tokenizer, texts: List[str]
    # ) -> np.ndarray:
    #     """Compute embeddings using MedCPT"""
    #     print(f"Computing embeddings for {len(texts)} texts with MedCPT...")
    #     logger.info(f"Computing MedCPT embeddings for {len(texts)} texts")
    #     import torch

    #     start_time = time.time()
    #     target_device = self.secondary_device if self.use_multi_gpu else self.device
    #     if target_device and target_device.type == "cuda":
    #         model = model.to(target_device)
    #     processed_texts = [
    #         re.sub(r"[^\w\s\.\,\;\:\!\?\-\(\)]", " ", str(text).strip() or "empty text")
    #         for text in texts
    #     ]
    #     batch_size = 32 if target_device and target_device.type == "cuda" else 16
    #     all_embeddings = []

    #     for i in tqdm(
    #         range(0, len(processed_texts), batch_size), desc="Processing MedCPT batches"
    #     ):
    #         batch_texts = processed_texts[i : i + batch_size]
    #         try:
    #             encoded = tokenizer(
    #                 batch_texts,
    #                 truncation=True,
    #                 padding=True,
    #                 return_tensors="pt",
    #                 max_length=128,
    #             )
    #             if target_device and target_device.type == "cuda":
    #                 encoded = {k: v.to(target_device) for k, v in encoded.items()}
    #             with torch.no_grad():
    #                 output = model(**encoded)
    #                 cls_embeddings = output.last_hidden_state[:, 0, :].cpu().numpy()
    #                 all_embeddings.append(cls_embeddings)
    #         except Exception as e:
    #             logger.warning(f"Error in batch {i//batch_size + 1}: {e}")
    #             all_embeddings.append(np.zeros((len(batch_texts), 768)))

    #     embeddings = (
    #         np.concatenate(all_embeddings, axis=0)
    #         if all_embeddings
    #         else np.zeros((len(texts), 768))
    #     )
    #     print(
    #         f"Completed MedCPT embeddings in {time.time() - start_time:.2f} seconds, shape: {embeddings.shape}"
    #     )
    #     logger.info(f"MedCPT embeddings shape: {embeddings.shape}")
    #     return embeddings

    # def compute_embeddings(self, model_name: str, texts: List[str]) -> np.ndarray:
    #     if model_name == "all-MiniLM-L6-v2":
    #         return self.compute_embeddings_sentence_transformer(
    #             self.embedding_models[model_name], texts
    #         )
    #     elif model_name == "SAPBERT":
    #         return self.compute_embeddings_transformers(
    #             self.embedding_models[model_name], self.tokenizers[model_name], texts
    #         )
    #     elif model_name == "MedCPT":
    #         return self.compute_embeddings_medcpt(
    #             self.embedding_models[model_name], self.tokenizers[model_name], texts
    #         )
    #     raise ValueError(f"Unknown model: {model_name}")
