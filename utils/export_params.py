"""Export functionality for analysis parameters, figures, and bundles."""

import os
import platform
import sys
import tempfile
import yaml
import zipfile
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union

import plotly.graph_objects as go  # type: ignore


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


def _detect_archive_format() -> str:
    """Detect the appropriate archive format based on OS.

    Returns:
        "tar.gz" for Linux/Mac, "zip" for Windows
    """
    system = platform.system().lower()
    if system == "windows":
        return "zip"
    return "tar.gz"


def export_figure_png(
    figure: Union[go.Figure, Dict[str, Any]],
    output_dir: str = ".",
    dpi: int = 400,
    timestamp: Optional[str] = None,
) -> str:
    """Export Plotly figure to PNG at specified DPI with proper font scaling.

    Unlike R where DPI affects font rendering directly, Plotly renders at
    screen resolution and then scales. We use the `scale` parameter to achieve
    higher DPI output while maintaining proper font proportions.

    At 400 DPI for print:
    - Base figure: 700px height (~7 inches at 100 DPI screen)
    - Scale factor: 400/100 = 4x
    - Output: ~2800px height = 7 inches at 400 DPI

    Args:
        figure: Plotly Figure object or figure dict from Dash callback
        output_dir: Directory to save the file
        dpi: Dots per inch for the output (default 400)
        timestamp: Optional timestamp string; if None, generates one

    Returns:
        Path to the created PNG file

    Raises:
        ImportError: If kaleido is not installed
    """
    try:
        import kaleido  # noqa: F401 - verify kaleido is available
    except ImportError:
        raise ImportError(
            "kaleido is required for PNG export. "
            "Install it with: pip install kaleido>=0.2.1"
        )

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")

    filename = f"{timestamp}-figure.png"
    filepath = Path(output_dir) / filename

    # Convert dict to Figure if necessary (from Dash callback)
    if isinstance(figure, dict):
        figure = go.Figure(figure)

    # Use Plotly's scale parameter for proper high-DPI export
    # This scales everything uniformly (fonts, lines, markers) so
    # relative proportions are maintained like in R's high-DPI export.
    #
    # Base assumption: screen is ~100 DPI, so scale = target_dpi / 100
    # For 400 DPI: scale = 4
    base_dpi = 100
    scale_factor = dpi / base_dpi

    # Get base dimensions from figure (or use defaults)
    base_width = 1000  # ~10 inches at 100 DPI
    base_height = figure.layout.height or 700

    figure.write_image(
        str(filepath),
        format="png",
        width=base_width,
        height=int(base_height),
        scale=scale_factor,
        engine="kaleido",
    )

    return str(filepath)


def create_export_bundle(
    yaml_path: str,
    png_path: str,
    output_dir: str = ".",
    archive_format: str = "auto",
    timestamp: Optional[str] = None,
) -> str:
    """Bundle YAML params and PNG figure into an archive.

    Args:
        yaml_path: Path to the YAML parameters file
        png_path: Path to the PNG figure file
        output_dir: Directory to save the archive
        archive_format: "auto" (detect OS), "zip", or "tar.gz"
        timestamp: Optional timestamp string; if None, generates one

    Returns:
        Path to the created archive file
    """
    if timestamp is None:
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")

    if archive_format == "auto":
        archive_format = _detect_archive_format()

    if archive_format == "zip":
        archive_name = f"{timestamp}-export.zip"
        archive_path = Path(output_dir) / archive_name

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(yaml_path, Path(yaml_path).name)
            zf.write(png_path, Path(png_path).name)

    elif archive_format == "tar.gz":
        archive_name = f"{timestamp}-export.tar.gz"
        archive_path = Path(output_dir) / archive_name

        with tarfile.open(archive_path, "w:gz") as tf:
            tf.add(yaml_path, arcname=Path(yaml_path).name)
            tf.add(png_path, arcname=Path(png_path).name)

    else:
        raise ValueError(f"Unsupported archive format: {archive_format}")

    return str(archive_path)


def export_analysis_package(
    figure: Union[go.Figure, Dict[str, Any]],
    dim_method: str,
    dim_params: Dict[str, Any],
    cluster_method: str,
    cluster_params: Dict[str, Any],
    model_name: Optional[str] = None,
    output_dir: str = ".",
    dpi: int = 400,
    archive_format: str = "auto",
) -> str:
    """Export complete analysis package: YAML + PNG bundled into archive.

    This is a convenience function that combines all export steps:
    1. Export parameters to YAML
    2. Export figure to PNG at specified DPI
    3. Bundle both into a zip or tar.gz archive

    Args:
        figure: Plotly Figure object or figure dict
        dim_method: Dimension reduction method ID
        dim_params: Dimension reduction parameters
        cluster_method: Clustering method ID
        cluster_params: Clustering parameters
        model_name: Optional embedding model name
        output_dir: Directory to save all files
        dpi: Dots per inch for PNG (default 400)
        archive_format: "auto" (detect OS), "zip", or "tar.gz"

    Returns:
        Path to the created archive file
    """
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")

    # Use temp directory for intermediate files
    with tempfile.TemporaryDirectory() as temp_dir:
        # Export YAML
        yaml_path = export_params_yaml(
            dim_method=dim_method,
            dim_params=dim_params,
            cluster_method=cluster_method,
            cluster_params=cluster_params,
            output_dir=temp_dir,
            model_name=model_name,
        )

        # Export PNG
        png_path = export_figure_png(
            figure=figure,
            output_dir=temp_dir,
            dpi=dpi,
            timestamp=timestamp,
        )

        # Create archive
        archive_path = create_export_bundle(
            yaml_path=yaml_path,
            png_path=png_path,
            output_dir=output_dir,
            archive_format=archive_format,
            timestamp=timestamp,
        )

    return archive_path
