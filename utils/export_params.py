"""YAML export functionality for analysis parameters."""

import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


def export_params_yaml(
    dim_method: str,
    dim_params: Dict[str, Any],
    cluster_method: str,
    cluster_params: Dict[str, Any],
    output_dir: str = ".",
    model_name: Optional[str] = None,
) -> str:
    """Export current parameters to a YAML file.

    Args:
        dim_method: Dimension reduction method ID (e.g., "umap")
        dim_params: Dimension reduction parameters
        cluster_method: Clustering method ID (e.g., "hdbscan")
        cluster_params: Clustering parameters
        output_dir: Directory to save the file
        model_name: Optional model name to include in export

    Returns:
        Path to the created YAML file
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    filename = f"{timestamp}-params.yaml"
    filepath = Path(output_dir) / filename

    params_dict: Dict[str, Any] = {
        "exported_at": datetime.now().isoformat(),
        "dimension_reduction": {
            "method": dim_method,
            "parameters": dim_params,
        },
        "clustering": {
            "method": cluster_method,
            "parameters": cluster_params,
        },
    }

    if model_name:
        params_dict["embedding_model"] = model_name

    with open(filepath, "w", encoding="utf-8") as f:
        yaml.dump(params_dict, f, default_flow_style=False, sort_keys=False)

    return str(filepath)


def load_params_yaml(filepath: str) -> Dict[str, Any]:
    """Load parameters from a YAML file.

    Args:
        filepath: Path to the YAML file

    Returns:
        Dictionary containing the loaded parameters
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
