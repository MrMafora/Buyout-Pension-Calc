#!/bin/bash
#
# test-tools.sh - Test OpenClaw tool availability
# Usage: ./test-tools.sh [options]
# Options:
#   --tool <name>   Test specific tool only
#   --verbose       Show detailed output
#   --quiet         Minimal output
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Options
SPECIFIC_TOOL=""
VERBOSE=0
QUIET=0
TIMEOUT=30

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --tool) SPECIFIC_TOOL="$2"; shift 2 ;;
    --verbose) VERBOSE=1; shift ;;
    --quiet) QUIET=1; shift ;;
    --timeout) TIMEOUT="$2"; shift 2 ;;
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

# Tool definitions with test commands
declare -A TOOLS
declare -A TOOL_DESCRIPTIONS

TOOLS[read]="test -f /root/.openclaw/workspace/AGENTS.md"
TOOL_DESCRIPTIONS[read]="File reading operations"

TOOLS[write]="echo 'test' > /tmp/tool-tester-write-test.txt && rm -f /tmp/tool-tester-write-test.txt"
TOOL_DESCRIPTIONS[write]="File writing operations"

TOOLS[edit]="test -f /root/.openclaw/workspace/AGENTS.md"
TOOL_DESCRIPTIONS[edit]="File editing operations"

TOOLS[exec]="uname -a > /dev/null"
TOOL_DESCRIPTIONS[exec]="Shell command execution"

TOOLS[process]="ps aux > /dev/null"
TOOL_DESCRIPTIONS[process]="Process management"

TOOLS[web_search]="which curl > /dev/null || which wget > /dev/null"
TOOL_DESCRIPTIONS[web_search]="Web search functionality"

TOOLS[web_fetch]="which curl > /dev/null || which wget > /dev/null"
TOOL_DESCRIPTIONS[web_fetch]="URL content fetching"

TOOLS[browser]="test -x /snap/bin/chromium || which chromium > /dev/null"
TOOL_DESCRIPTIONS[browser]="Browser automation"

TOOLS[canvas]="test -d /root/.openclaw/workspace"
TOOL_DESCRIPTIONS[canvas]="Canvas operations"

TOOLS[nodes]="test -d /root/.openclaw/workspace"
TOOL_DESCRIPTIONS[nodes]="Node management"

TOOLS[message]="test -f /root/.openclaw/workspace/AGENTS.md"
TOOL_DESCRIPTIONS[message]="Messaging channels"

TOOLS[image]="which file > /dev/null"
TOOL_DESCRIPTIONS[image]="Image analysis"

TOOLS[tts]="which edge-tts > /dev/null 2>&1 || test -x /usr/bin/tts"
TOOL_DESCRIPTIONS[tts]="Text-to-speech"

# Test a single tool
test_tool() {
  local name="$1"
  local cmd="${TOOLS[$name]}"
  local desc="${TOOL_DESCRIPTIONS[$name]}"
  
  detail "${BLUE}Testing $name...${NC}"
  detail "  Description: $desc"
  
  if timeout "$TIMEOUT" bash -c "$cmd" > /dev/null 2>&1; then
    detail "  ${GREEN}✓ Available${NC}"
    return 0
  else
    detail "  ${RED}✗ Not available${NC}"
    return 1
  fi
}

# Main execution
PASS_COUNT=0
FAIL_COUNT=0

if [[ -n "$SPECIFIC_TOOL" ]]; then
  if [[ -z "${TOOLS[$SPECIFIC_TOOL]}" ]]; then
    echo "Unknown tool: $SPECIFIC_TOOL"
    exit 2
  fi
  
  if test_tool "$SPECIFIC_TOOL"; then
    echo "${GREEN}✓ $SPECIFIC_TOOL is available${NC}"
    exit 0
  else
    echo "${RED}✗ $SPECIFIC_TOOL is not available${NC}"
    exit 1
  fi
fi

log "${BLUE}Testing OpenClaw Tools...${NC}"
log ""

for tool in "${!TOOLS[@]}"; do
  if test_tool "$tool"; then
    log "${GREEN}✓${NC} $tool"
    PASS_COUNT=$((PASS_COUNT + 1))
  else
    log "${RED}✗${NC} $tool"
    FAIL_COUNT=$((FAIL_COUNT + 1))
  fi
done

log ""
log "Results: ${GREEN}$PASS_COUNT passed${NC}, ${RED}$FAIL_COUNT failed${NC}"

if [[ $FAIL_COUNT -gt 0 ]]; then
  exit 1
else
  exit 0
fi
