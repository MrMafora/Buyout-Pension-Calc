#!/bin/bash
#
# validate-env.sh - Validate environment setup
# Usage: ./validate-env.sh [options]
# Options:
#   --check-deps    Check dependencies
#   --check-keys    Check API keys
#   --fix           Attempt to fix issues
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
CHECK_DEPS=1
CHECK_KEYS=0
FIX_MODE=0
VERBOSE=0
QUIET=0

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --check-deps) CHECK_DEPS=1; shift ;;
    --check-keys) CHECK_KEYS=1; shift ;;
    --fix) FIX_MODE=1; shift ;;
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

# Track results
PASS_COUNT=0
FAIL_COUNT=0
WARNING_COUNT=0

check_pass() {
  log "${GREEN}✓${NC} $1"
  PASS_COUNT=$((PASS_COUNT + 1))
}

check_fail() {
  log "${RED}✗${NC} $1"
  FAIL_COUNT=$((FAIL_COUNT + 1))
}

check_warn() {
  log "${YELLOW}⚠${NC} $1"
  WARNING_COUNT=$((WARNING_COUNT + 1))
}

# Check Node.js version
check_node() {
  detail "${BLUE}Checking Node.js...${NC}"
  
  if command -v node > /dev/null 2>&1; then
    local version=$(node --version 2>/dev/null | sed 's/v//')
    detail "  Version: $version"
    
    # Check if version is >= 18.0.0
    local major=$(echo "$version" | cut -d. -f1)
    if [[ "$major" -ge 18 ]]; then
      check_pass "Node.js $version"
    else
      check_warn "Node.js $version (recommend v18+)"
    fi
  else
    check_fail "Node.js not found"
  fi
}

# Check required binaries
check_binaries() {
  detail "${BLUE}Checking binaries...${NC}"
  
  local binaries=("curl" "git" "python3" "pip3")
  
  for bin in "${binaries[@]}"; do
    if command -v "$bin" > /dev/null 2>&1; then
      local path=$(which "$bin")
      detail "  $bin: $path"
      check_pass "$bin"
    else
      check_fail "$bin not found"
    fi
  done
  
  # Check optional binaries
  local optional=("chromium" "ffmpeg" "edge-tts")
  
  for bin in "${optional[@]}"; do
    if command -v "$bin" > /dev/null 2>&1; then
      detail "  $bin: found"
      check_pass "$bin"
    else
      detail "  $bin: not found (optional)"
    fi
  done
}

# Check workspace structure
check_workspace() {
  detail "${BLUE}Checking workspace...${NC}"
  
  if [[ -d "$WORKSPACE_DIR" ]]; then
    check_pass "Workspace directory"
  else
    check_fail "Workspace directory not found"
    return
  fi
  
  # Check essential files
  local files=("AGENTS.md" "TOOLS.md")
  
  for file in "${files[@]}"; do
    if [[ -f "$WORKSPACE_DIR/$file" ]]; then
      check_pass "$file"
    else
      check_warn "$file not found"
    fi
  done
  
  # Check directories
  local dirs=("skills" "memory")
  
  for dir in "${dirs[@]}"; do
    if [[ -d "$WORKSPACE_DIR/$dir" ]]; then
      check_pass "$dir/ directory"
    else
      check_warn "$dir/ directory not found"
      
      if [[ $FIX_MODE -eq 1 ]]; then
        mkdir -p "$WORKSPACE_DIR/$dir"
        log "  ${BLUE}Created $dir/ directory${NC}"
      fi
    fi
  done
}

# Check environment variables
check_env_vars() {
  detail "${BLUE}Checking environment...${NC}"
  
  # Check HOME
  if [[ -n "$HOME" ]]; then
    check_pass "HOME set"
  else
    check_fail "HOME not set"
  fi
  
  # Check PATH
  if [[ -n "$PATH" ]]; then
    check_pass "PATH set"
  else
    check_fail "PATH not set"
  fi
  
  # Check OpenClaw specific
  if [[ -d "$HOME/.openclaw" ]]; then
    check_pass "OpenClaw directory exists"
  else
    check_warn "OpenClaw directory not found"
  fi
}

# Check API keys (if requested)
check_api_keys() {
  detail "${BLUE}Checking API keys...${NC}"
  
  local keys=("BRAVE_API_KEY" "RESEND_API_KEY")
  
  for key in "${keys[@]}"; do
    if [[ -n "${!key}" ]]; then
      check_pass "$key set"
    else
      check_warn "$key not set"
    fi
  done
}

# Check permissions
check_permissions() {
  detail "${BLUE}Checking permissions...${NC}"
  
  if [[ -w "$WORKSPACE_DIR" ]]; then
    check_pass "Workspace writable"
  else
    check_fail "Workspace not writable"
  fi
  
  if [[ -w "/tmp" ]]; then
    check_pass "/tmp writable"
  else
    check_fail "/tmp not writable"
  fi
}

# Main execution
log "${BLUE}Validating Environment...${NC}"
log ""

check_node
check_binaries
check_workspace
check_env_vars
check_permissions

if [[ $CHECK_KEYS -eq 1 ]]; then
  check_api_keys
fi

log ""
log "Results: ${GREEN}$PASS_COUNT passed${NC}, ${RED}$FAIL_COUNT failed${NC}, ${YELLOW}$WARNING_COUNT warnings${NC}"

if [[ $FAIL_COUNT -gt 0 ]]; then
  exit 1
else
  exit 0
fi
