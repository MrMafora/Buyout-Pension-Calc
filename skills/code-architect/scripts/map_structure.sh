#!/bin/bash
# Generate a project structure map using 'tree' or 'find'
# Usage: ./map_structure.sh [directory]

TARGET_DIR="${1:-.}"

if ! command -v tree &> /dev/null; then
    echo "Warning: 'tree' command not found. Falling back to 'find'."
    find "$TARGET_DIR" -maxdepth 3 -not -path '*/.*' | sed -e "s/[^-][^\/]*\// |/g" -e "s/|\([^ ]\)/|-\1/"
else
    # Exclude common noise directories
    tree "$TARGET_DIR" -I 'node_modules|dist|build|coverage|.git|.idea|.vscode|__pycache__|venv' --dirsfirst -L 3
fi
