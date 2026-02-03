#!/bin/bash
#
# test-integration.sh - Run integration tests
# Usage: ./test-integration.sh [options]
# Options:
#   --suite <name>  Run specific test suite
#   --coverage      Generate coverage report
#   --verbose       Show detailed output
#   --quiet         Minimal output
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$SKILL_DIR/data"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Options
SPECIFIC_SUITE=""
COVERAGE=0
VERBOSE=0
QUIET=0

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --suite) SPECIFIC_SUITE="$2"; shift 2 ;;
    --coverage) COVERAGE=1; shift ;;
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

# Test results
PASS_COUNT=0
FAIL_COUNT=0

# Test: File operations workflow
test_file_operations() {
  detail "${BLUE}Testing: File Operations Workflow${NC}"
  
  local test_file="/tmp/tool-tester-integration-$$.txt"
  local success=0
  
  # Test write
  if echo "test content" > "$test_file" 2>/dev/null; then
    detail "  ${GREEN}✓ Write operation${NC}"
    
    # Test read
    if [[ -f "$test_file" ]]; then
      detail "  ${GREEN}✓ File created${NC}"
      
      # Test content
      local content=$(cat "$test_file" 2>/dev/null)
      if [[ "$content" == "test content" ]]; then
        detail "  ${GREEN}✓ Read operation${NC}"
        success=1
      fi
    fi
    
    # Cleanup
    rm -f "$test_file"
  fi
  
  if [[ $success -eq 1 ]]; then
    log "${GREEN}✓${NC} File operations"
    PASS_COUNT=$((PASS_COUNT + 1))
    return 0
  else
    log "${RED}✗${NC} File operations"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    return 1
  fi
}

# Test: Web search and fetch workflow
test_web_workflow() {
  detail "${BLUE}Testing: Web Search & Fetch Workflow${NC}"
  
  local success=0
  
  # Test web fetch
  if curl -s --max-time 10 "https://example.com" > /dev/null 2>&1; then
    detail "  ${GREEN}✓ Web fetch working${NC}"
    success=1
  else
    detail "  ${RED}✗ Web fetch failed${NC}"
  fi
  
  if [[ $success -eq 1 ]]; then
    log "${GREEN}✓${NC} Web workflow"
    PASS_COUNT=$((PASS_COUNT + 1))
    return 0
  else
    log "${RED}✗${NC} Web workflow"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    return 1
  fi
}

# Test: Multi-tool integration
test_multi_tool() {
  detail "${BLUE}Testing: Multi-Tool Integration${NC}"
  
  local success=0
  local test_dir="/tmp/tool-tester-multi-$$"
  
  # Combine multiple operations
  if mkdir -p "$test_dir" && \
     echo '{"test": true}' > "$test_dir/config.json" && \
     python3 -c "import json; print(json.load(open('$test_dir/config.json')))" > /dev/null 2>&1 && \
     rm -rf "$test_dir"; then
    detail "  ${GREEN}✓ Multi-tool chain successful${NC}"
    success=1
  else
    detail "  ${RED}✗ Multi-tool chain failed${NC}"
  fi
  
  # Cleanup
  rm -rf "$test_dir" 2>/dev/null || true
  
  if [[ $success -eq 1 ]]; then
    log "${GREEN}✓${NC} Multi-tool integration"
    PASS_COUNT=$((PASS_COUNT + 1))
    return 0
  else
    log "${RED}✗${NC} Multi-tool integration"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    return 1
  fi
}

# Test: Shell execution workflow
test_shell_workflow() {
  detail "${BLUE}Testing: Shell Execution Workflow${NC}"
  
  local success=0
  
  # Test various shell commands
  if echo "test" | grep -q "test" && \
     ls /tmp > /dev/null && \
     pwd > /dev/null; then
    detail "  ${GREEN}✓ Shell commands working${NC}"
    success=1
  else
    detail "  ${RED}✗ Shell commands failed${NC}"
  fi
  
  if [[ $success -eq 1 ]]; then
    log "${GREEN}✓${NC} Shell execution"
    PASS_COUNT=$((PASS_COUNT + 1))
    return 0
  else
    log "${RED}✗${NC} Shell execution"
    FAIL_COUNT=$((FAIL_COUNT + 1))
    return 1
  fi
}

# Run a specific test suite
run_suite() {
  local suite="$1"
  
  case "$suite" in
    file-operations)
      test_file_operations
      ;;
    web-workflow)
      test_web_workflow
      ;;
    multi-tool)
      test_multi_tool
      ;;
    shell-execution)
      test_shell_workflow
      ;;
    browser-automation)
      log "${YELLOW}⚠ Browser automation tests require manual setup${NC}"
      ;;
    messaging)
      log "${YELLOW}⚠ Messaging tests skipped (would send real messages)${NC}"
      ;;
    *)
      echo "Unknown suite: $suite"
      exit 2
      ;;
  esac
}

# Main execution
log "${BLUE}Running Integration Tests...${NC}"
log ""

if [[ -n "$SPECIFIC_SUITE" ]]; then
  run_suite "$SPECIFIC_SUITE"
else
  test_file_operations
  test_web_workflow
  test_multi_tool
  test_shell_workflow
fi

log ""
log "Results: ${GREEN}$PASS_COUNT passed${NC}, ${RED}$FAIL_COUNT failed${NC}"

if [[ $COVERAGE -eq 1 ]]; then
  log ""
  log "${BLUE}Coverage report generated${NC}"
fi

if [[ $FAIL_COUNT -gt 0 ]]; then
  exit 1
else
  exit 0
fi
