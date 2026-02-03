#!/bin/bash
#
# run-all-tests.sh - Run all tool-tester tests
# Usage: ./run-all-tests.sh [options]
# Options:
#   --quiet         Suppress output except for final results
#   --comprehensive Run comprehensive tests (slower)
#   --report        Generate report after tests
#   --format        Report format (html|json|markdown)
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$SKILL_DIR/data"
RESULTS_DIR="$DATA_DIR/test-results"
LOGS_DIR="$RESULTS_DIR/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Options
QUIET=0
COMPREHENSIVE=0
GENERATE_REPORT=0
REPORT_FORMAT="markdown"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --quiet) QUIET=1; shift ;;
    --comprehensive) COMPREHENSIVE=1; shift ;;
    --report) GENERATE_REPORT=1; shift ;;
    --format) REPORT_FORMAT="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 2 ;;
  esac
done

# Logging function
log() {
  if [[ $QUIET -eq 0 ]]; then
    echo -e "$@"
  fi
}

# Create directories
mkdir -p "$RESULTS_DIR" "$LOGS_DIR"

# Test results
declare -A TEST_RESULTS
declare -A TEST_TIMES
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOGS_DIR/test-run-$TIMESTAMP.log"

log "${BLUE}========================================${NC}"
log "${BLUE}  OpenClaw Tool Tester - Test Suite${NC}"
log "${BLUE}========================================${NC}"
log ""
log "Started: $(date)"
log "Log file: $LOG_FILE"
log ""

# Run a test script and capture result
run_test() {
  local name="$1"
  local script="$2"
  local args="${3:-}"
  
  TOTAL_TESTS=$((TOTAL_TESTS + 1))
  
  log "${BLUE}▶ Running: $name${NC}"
  
  local start_time=$(date +%s)
  
  if [[ $QUIET -eq 1 ]]; then
    if bash "$script" $args --quiet >> "$LOG_FILE" 2>&1; then
      local end_time=$(date +%s)
      TEST_TIMES[$name]=$((end_time - start_time))
      TEST_RESULTS[$name]="PASS"
      PASSED_TESTS=$((PASSED_TESTS + 1))
      log "${GREEN}  ✓ PASS${NC} (${TEST_TIMES[$name]}s)"
      return 0
    else
      local end_time=$(date +%s)
      TEST_TIMES[$name]=$((end_time - start_time))
      TEST_RESULTS[$name]="FAIL"
      FAILED_TESTS=$((FAILED_TESTS + 1))
      log "${RED}  ✗ FAIL${NC} (${TEST_TIMES[$name]}s)"
      return 1
    fi
  else
    if bash "$script" $args 2>&1 | tee -a "$LOG_FILE"; then
      local end_time=$(date +%s)
      TEST_TIMES[$name]=$((end_time - start_time))
      TEST_RESULTS[$name]="PASS"
      PASSED_TESTS=$((PASSED_TESTS + 1))
      log "${GREEN}✓ $name passed${NC} (${TEST_TIMES[$name]}s)"
      return 0
    else
      local end_time=$(date +%s)
      TEST_TIMES[$name]=$((end_time - start_time))
      TEST_RESULTS[$name]="FAIL"
      FAILED_TESTS=$((FAILED_TESTS + 1))
      log "${RED}✗ $name failed${NC} (${TEST_TIMES[$name]}s)"
      return 1
    fi
  fi
}

# Run all test categories
log "${YELLOW}Running Tool Tests...${NC}"
run_test "Tools" "$SCRIPT_DIR/test-tools.sh"
log ""

log "${YELLOW}Running Script Tests...${NC}"
run_test "Scripts" "$SCRIPT_DIR/test-scripts.sh"
log ""

log "${YELLOW}Running API Tests...${NC}"
run_test "APIs" "$SCRIPT_DIR/test-apis.sh"
log ""

log "${YELLOW}Running Environment Validation...${NC}"
run_test "Environment" "$SCRIPT_DIR/validate-env.sh"
log ""

if [[ $COMPREHENSIVE -eq 1 ]]; then
  log "${YELLOW}Running Integration Tests...${NC}"
  run_test "Integration" "$SCRIPT_DIR/test-integration.sh"
  log ""
  
  log "${YELLOW}Running Browser Tests...${NC}"
  run_test "Browser" "$SCRIPT_DIR/test-browser.sh"
  log ""
  
  log "${YELLOW}Running Messaging Tests...${NC}"
  run_test "Messaging" "$SCRIPT_DIR/test-messaging.sh"
  log ""
fi

# Summary
log ""
log "${BLUE}========================================${NC}"
log "${BLUE}  Test Summary${NC}"
log "${BLUE}========================================${NC}"
log ""
log "Total Tests:  $TOTAL_TESTS"
log "${GREEN}Passed:       $PASSED_TESTS${NC}"
log "${RED}Failed:       $FAILED_TESTS${NC}"
log "${YELLOW}Skipped:      $SKIPPED_TESTS${NC}"
log ""

# Save JSON results
cat > "$RESULTS_DIR/latest.json" << EOF
{
  "timestamp": "$TIMESTAMP",
  "date": "$(date -Iseconds)",
  "summary": {
    "total": $TOTAL_TESTS,
    "passed": $PASSED_TESTS,
    "failed": $FAILED_TESTS,
    "skipped": $SKIPPED_TESTS
  },
  "results": {
$(for name in "${!TEST_RESULTS[@]}"; do
  echo "    \"$name\": {"
  echo "      \"status\": \"${TEST_RESULTS[$name]}\","
  echo "      \"duration\": ${TEST_TIMES[$name]}"
  echo "    },"
done | sed '$ s/,$//')
  }
}
EOF

log "Results saved to: $RESULTS_DIR/latest.json"
log "Full log: $LOG_FILE"
log ""

# Generate report if requested
if [[ $GENERATE_REPORT -eq 1 ]]; then
  log "${YELLOW}Generating report...${NC}"
  bash "$SCRIPT_DIR/generate-report.sh" --format "$REPORT_FORMAT" --input "$RESULTS_DIR/latest.json"
  log ""
fi

log "Completed: $(date)"

# Exit with appropriate code
if [[ $FAILED_TESTS -gt 0 ]]; then
  exit 1
else
  exit 0
fi
