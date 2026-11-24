#!/bin/bash
# Wrapper script that ensures venv is set up before running Python scripts
# Usage: ./run.sh <script.py> [args...]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/.venv"

REQUIREMENTS="$SKILL_DIR/requirements.txt"
STAMP="$VENV_DIR/.installed-requirements.txt"

# Create the venv if needed, and (re)install packages whenever requirements.txt changes,
# so existing installs pick up new pinned versions
if [ ! -f "$VENV_DIR/bin/python" ]; then
    echo "Setting up virtual environment..." >&2
    python3 -m venv "$VENV_DIR"
fi
if ! cmp -s "$REQUIREMENTS" "$STAMP"; then
    echo "Installing pinned packages..." >&2
    "$VENV_DIR/bin/pip" install --quiet -r "$REQUIREMENTS"
    cp "$REQUIREMENTS" "$STAMP"
    echo "Setup complete." >&2
fi

# Run the requested script with all arguments
SCRIPT="$1"
shift
exec "$VENV_DIR/bin/python" "$SCRIPT_DIR/$SCRIPT" "$@"
