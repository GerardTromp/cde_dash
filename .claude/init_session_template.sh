#!/bin/bash
# Claude Code Session Initialization Script
# This file is NOT tracked by git - contains local environment specifics
#
# Usage: source .claude/init_session.sh
#
# Run this after:
#   - Starting a new Claude Code session
#   - After /compact or context reset
#   - When commands fail due to missing environment

# =============================================================================
# CONFIGURATION - Update these placeholders after venv creation
# =============================================================================

# Python virtual environment path
# TODO: Update after creating venv with: python -m venv /path/to/venv
VENV_PATH="/home/<USER>/venv/<VENV_NAME>/bin/activate"

# Project root directory (where this repo is cloned)
DASH_CLUST="/home/<USER>/<PATH_TO_CODE>/clust_app"

# =============================================================================
# ENVIRONMENT ACTIVATION
# =============================================================================

echo "=== Claude Code Session Initialization ==="

# 1. Activate Python virtual environment
if [ -f "${VENV_PATH}" ]; then
    source "${VENV_PATH}"
    echo "[OK] Python venv activated: $(which python)"
    echo "     Python version: $(python --version 2>&1)"
else
    echo "[WARN] Venv not found at: ${VENV_PATH}"
    echo "       Update VENV_PATH in this script after creating venv"
fi

# 2. Export project path
export DASH_CLUST="${DASH_CLUST}"
echo "[OK] DASH_CLUST set to: ${DASH_CLUST}"

# 3. Verify we're in the right directory or can access it
if [ -d "${DASH_CLUST}" ]; then
    echo "[OK] Project directory exists"
else
    echo "[WARN] Project directory not found: ${DASH_CLUST}"
fi

# =============================================================================
# OPTIONAL: Spack modules (if needed in future)
# =============================================================================
# Currently none required
# Example: module load python/3.11

# =============================================================================
# VERIFICATION
# =============================================================================

echo ""
echo "--- Environment Check ---"

# Check Python packages (quick sanity check)
if command -v python &> /dev/null; then
    python -c "import dash; print(f'[OK] Dash version: {dash.__version__}')" 2>/dev/null || \
        echo "[WARN] Dash not installed in current environment"
    python -c "import pandas; print(f'[OK] Pandas version: {pandas.__version__}')" 2>/dev/null || \
        echo "[WARN] Pandas not installed in current environment"
else
    echo "[WARN] Python not available"
fi

echo ""
echo "=== Initialization Complete ==="
echo ""
echo "Quick commands:"
echo "  cd \${DASH_CLUST}              # Go to project directory"
echo "  python \${DASH_CLUST}/domains_clustering_interactive_plots_dash.py --help"
echo ""
