#!/bin/bash
#===============================================================================
#  HOME-PLEX UNINSTALLER
#  Installs uv if needed and runs the uninstall script
#===============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install uv if not available
if ! command -v uv &> /dev/null; then
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Run the uninstall script with uv
exec uv run "$SCRIPT_DIR/scripts/uninstall.py"
