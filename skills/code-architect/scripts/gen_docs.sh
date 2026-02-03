#!/bin/bash
# Generate a README stub based on project content
# Usage: ./gen_docs.sh [directory]

TARGET_DIR="${1:-.}"
PROJECT_NAME=$(basename "$(realpath "$TARGET_DIR")")

echo "# $PROJECT_NAME"
echo ""
echo "## Overview"
echo "(Auto-generated stub. Description goes here.)"
echo ""

if [ -f "$TARGET_DIR/package.json" ]; then
    echo "## Installation (Node.js)"
    echo "\`\`\`bash"
    echo "npm install"
    echo "\`\`\`"
    echo ""
    echo "## Scripts"
    grep '"scripts":' -A 10 "$TARGET_DIR/package.json" | sed '1d' | head -n -1 | sed 's/^[[:space:]]*//'
fi

if [ -f "$TARGET_DIR/requirements.txt" ]; then
    echo "## Installation (Python)"
    echo "\`\`\`bash"
    echo "pip install -r requirements.txt"
    echo "\`\`\`"
fi

if [ -f "$TARGET_DIR/go.mod" ]; then
    echo "## Installation (Go)"
    echo "\`\`\`bash"
    echo "go mod download"
    echo "\`\`\`"
fi

echo ""
echo "## Structure"
if command -v tree &> /dev/null; then
    tree "$TARGET_DIR" -I 'node_modules|dist|build|.git' -L 2
else
    echo "(Install 'tree' for structure view)"
fi
