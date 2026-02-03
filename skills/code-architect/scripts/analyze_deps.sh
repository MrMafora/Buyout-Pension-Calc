#!/bin/bash
# Analyze dependencies in a project
# Usage: ./analyze_deps.sh [directory]

TARGET_DIR="${1:-.}"
echo "Analyzing dependencies in $TARGET_DIR..."

# Check for Node.js
if [ -f "$TARGET_DIR/package.json" ]; then
    echo "--- Node.js (package.json) ---"
    grep -A 50 '"dependencies":' "$TARGET_DIR/package.json" | grep -m 1 -B 50 '}' || echo "Could not parse dependencies cleanly."
    echo ""
    echo "--- Dev Dependencies ---"
    grep -A 50 '"devDependencies":' "$TARGET_DIR/package.json" | grep -m 1 -B 50 '}' || echo "Could not parse devDependencies cleanly."
fi

# Check for Python
if [ -f "$TARGET_DIR/requirements.txt" ]; then
    echo ""
    echo "--- Python (requirements.txt) ---"
    head -n 20 "$TARGET_DIR/requirements.txt"
    if [ $(wc -l < "$TARGET_DIR/requirements.txt") -gt 20 ]; then echo "... (truncated)"; fi
fi

if [ -f "$TARGET_DIR/pyproject.toml" ]; then
    echo ""
    echo "--- Python (pyproject.toml) ---"
    grep -A 20 "\[tool.poetry.dependencies\]" "$TARGET_DIR/pyproject.toml" || grep -A 20 "dependencies =" "$TARGET_DIR/pyproject.toml"
fi

# Check for Go
if [ -f "$TARGET_DIR/go.mod" ]; then
    echo ""
    echo "--- Go (go.mod) ---"
    grep -v "indirect" "$TARGET_DIR/go.mod" | grep "require"
fi
