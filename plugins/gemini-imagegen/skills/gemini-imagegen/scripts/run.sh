#!/bin/bash
# Wrapper script that ensures venv is set up before running Python scripts
# Usage: ./run.sh <script.py> [args...]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/.venv"

# Create venv and install packages if needed
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Setting up virtual environment..." >&2
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet -r "$SKILL_DIR/requirements.txt"
    echo "Setup complete." >&2
fi

# Run the requested script with all arguments
SCRIPT="$1"
shift
exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/$SCRIPT" "$@"
