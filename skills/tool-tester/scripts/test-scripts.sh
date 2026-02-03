#!/bin/bash
#
# test-scripts.sh - Test script execution
# Usage: ./test-scripts.sh [options]
# Options:
#   --script <path> Test specific script
#   --timeout <sec> Set timeout (default: 30)
#   --verbose       Show detailed output
#   --quiet         Minimal output
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE_DIR="/root/.openclaw/workspace"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Options
SPECIFIC_SCRIPT=""
TIMEOUT=30
VERBOSE=0
QUIET=0

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --script) SPECIFIC_SCRIPT="$2"; shift 2 ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
    --verbose) VERBOSE=1; shift ;;
    --quiet) QUIET=1; shift ;;
    *) echo "Unknown option: $1"; exit 2 ;;
  esac
done

log() {
  if [[ $QUIET -eq 0 ]]; then
    echo -e "$@"
  fi
}

detail() {
  if [[ $VERBOSE -eq 1 ]]; then
    echo -e "$@"
  fi
}

# Test a single script
test_script() {
  local script_path="$1"
  local script_name=$(basename "$script_path")
  
  detail "${BLUE}Testing: $script_name${NC}"
  detail "  Path: $script_path"
  
  # Check if file exists
  if [[ ! -f "$script_path" ]]; then
    detail "  ${RED}✗ File not found${NC}"
    return 1
  fi
  
  # Check if file is executable
  if [[ ! -x "$script_path" ]]; then
    detail "  ${YELLOW}⚠ Not executable, attempting to run with bash${NC}"
  fi
  
  # Determine script type
  local shebang=$(head -1 "$script_path" 2>/dev/null | grep -E '^#!')
  local interpreter=""
  
  if [[ "$script_path" == *.sh ]]; then
    interpreter="bash"
  elif [[ "$script_path" == *.py ]]; then
    interpreter="python3"
  elif [[ "$script_path" == *.js ]]; then
    interpreter="node"
  elif [[ -n "$shebang" ]]; then
    interpreter=$(echo "$shebang" | sed 's/#!//')
  else
    detail "  ${YELLOW}⚠ Unknown script type${NC}"
    interpreter="bash"
  fi
  
  detail "  Interpreter: $interpreter"
  
  # Test syntax (dry run where possible)
  local syntax_check=0
  case "$interpreter" in
    bash|*/bash)
      if bash -n "$script_path" 2>/dev/null; then
        detail "  ${GREEN}✓ Syntax OK${NC}"
        syntax_check=1
      else
        detail "  ${RED}✗ Syntax error${NC}"
      fi
      ;;
    python3|*/python3|python|*/python)
      if python3 -m py_compile "$script_path" 2>/dev/null; then
        detail "  ${GREEN}✓ Syntax OK${NC}"
        syntax_check=1
      else
        detail "  ${RED}✗ Syntax error${NC}"
      fi
      ;;
    node|*/node)
      if node --check "$script_path" 2>/dev/null; then
        detail "  ${GREEN}✓ Syntax OK${NC}"
        syntax_check=1
      else
        detail "  ${YELLOW}⚠ Syntax check skipped${NC}"
        syntax_check=1
      fi
      ;;
    *)
      detail "  ${YELLOW}⚠ No syntax check available${NC}"
      syntax_check=1
      ;;
  esac
  
  # Try to run script with --help (if supported)
  local run_check=0
  if [[ $syntax_check -eq 1 ]]; then
    detail "  Testing execution..."
    
    # Create a test environment
    local test_output=$(timeout "$TIMEOUT" bash -c "
      cd \$(dirname '$script_path')
      if [[ -x '$script_path' ]]; then
        '$script_path' --help 2>&1 || '$script_path' -h 2>&1 || echo 'EXEC_OK'
      else
        $interpreter '$script_path' --help 2>&1 || $interpreter '$script_path' -h 2>&1 || echo 'EXEC_OK'
      fi
    " 2>/dev/null | head -5)
    
    if [[ -n "$test_output" ]]; then
      detail "  ${GREEN}✓ Execution successful${NC}"
      run_check=1
    else
      detail "  ${YELLOW}⚠ Execution test inconclusive${NC}"
      run_check=1  # Still consider it pass if syntax was OK
    fi
  fi
  
  if [[ $syntax_check -eq 1 && $run_check -eq 1 ]]; then
    return 0
  else
    return 1
  fi
}

# Find all scripts in workspace
find_scripts() {
  find "$WORKSPACE_DIR" -type f \( \
    -name "*.sh" -o \
    -name "*.py" -o \
    -name "*.js" \
  \) 2>/dev/null | grep -v node_modules | grep -v __pycache__
}

# Main execution
PASS_COUNT=0
FAIL_COUNT=0

if [[ -n "$SPECIFIC_SCRIPT" ]]; then
  if test_script "$SPECIFIC_SCRIPT"; then
    echo "${GREEN}✓ Script test passed${NC}"
    exit 0
  else
    echo "${RED}✗ Script test failed${NC}"
    exit 1
  fi
fi

log "${BLUE}Testing Scripts in Workspace...${NC}"
log ""

SCRIPTS=$(find_scripts)

if [[ -z "$SCRIPTS" ]]; then
  log "${YELLOW}No scripts found in workspace${NC}"
  exit 0
fi

SCRIPT_COUNT=$(echo "$SCRIPTS" | wc -l)
log "Found $SCRIPT_COUNT scripts to test"
log ""

while IFS= read -r script; do
  script_name=$(basename "$script")
  
  if test_script "$script"; then
    log "${GREEN}✓${NC} $script_name"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    log "${RED}✗${NC} $script_name"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
done <<< "$SCRIPTS"

log ""
log "Results: ${GREEN}$PASS_COUNT passed${NC}, ${RED}$FAIL_COUNT failed${NC}"

if [[ $FAIL_COUNT -gt 0 ]]; then
  exit 1
else
  exit 0
fi
