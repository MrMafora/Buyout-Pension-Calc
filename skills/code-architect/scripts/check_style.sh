#!/bin/bash
# Basic code style checker / linter suggester
# Usage: ./check_style.sh [directory]

TARGET_DIR="${1:-.}"
echo "Checking code style indicators in $TARGET_DIR..."

# Check for large files
echo "--- Large Files (>1000 lines) ---"
find "$TARGET_DIR" -type f -not -path '*/.*' -not -path '*/node_modules/*' -exec wc -l {} + | awk '$1 > 1000 {print $0}' | head -n 10

# Check for TODOs
echo ""
echo "--- TODOs / FIXMEs ---"
grep -rE "TODO|FIXME" "$TARGET_DIR" --exclude-dir={node_modules,dist,.git,venv} | head -n 10
if [ $(grep -rE "TODO|FIXME" "$TARGET_DIR" --exclude-dir={node_modules,dist,.git,venv} | wc -l) -gt 10 ]; then
    echo "... (more found)"
fi

# Simple indentation check (mixed tabs/spaces check is hard in bash cleanly, just checking for config)
echo ""
echo "--- Style Configs Found ---"
[ -f "$TARGET_DIR/.eslintrc*" ] && echo "✅ ESLint found"
[ -f "$TARGET_DIR/.prettierrc*" ] && echo "✅ Prettier found"
[ -f "$TARGET_DIR/pylintrc" ] && echo "✅ Pylint found"
[ -f "$TARGET_DIR/.editorconfig" ] && echo "✅ EditorConfig found"
